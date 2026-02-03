# ============================================
# TENNIS CLASS MANAGEMENT SYSTEM
# Versão 2.0 - Completamente Reformulado
# ============================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import os
import logging
from datetime import datetime, date, time as dt_time
from typing import Dict, Any, Optional, Tuple
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, validator, Field
from logging.handlers import RotatingFileHandler

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
def setup_logging() -> logging.Logger:
    """Configurar sistema de logs completo."""
    logger = logging.getLogger('tennis_class')
    logger.setLevel(logging.INFO)
    
    # Evitar logs duplicados
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        'tennis_class.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    
    # Formato detalhado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# Configuração da página Streamlit
st.set_page_config(
    page_title="TENNIS CLASS PRO",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Aranhacorp/Tennis-Class',
        'Report a bug': None,
        'About': "Sistema de Gestão de Aulas de Tênis v2.0"
    }
)

# ============================================
# 2. CLASSES DE GERENCIAMENTO
# ============================================

class StateManager:
    """Gerenciador de estado da aplicação."""
    
    def __init__(self):
        self._state_keys = [
            'pagina', 'pagamento_ativo', 'reserva_temp',
            'inicio_timer', 'admin_autenticado', 'erros_form',
            'rate_limits', 'cache_stats'
        ]
        
        # Inicializar estados
        for key in self._state_keys:
            if key not in st.session_state:
                if key == 'rate_limits':
                    st.session_state[key] = {}
                elif key == 'cache_stats':
                    st.session_state[key] = {}
                elif key == 'erros_form':
                    st.session_state[key] = {}
                else:
                    st.session_state[key] = None if key in ['reserva_temp', 'inicio_timer'] else False
    
    def reset_state(self, keys: Optional[list] = None) -> None:
        """Resetar estado específico ou completo."""
        if keys is None:
            keys = self._state_keys
        
        for key in keys:
            if key in st.session_state:
                if key == 'rate_limits':
                    st.session_state[key] = {}
                elif key == 'cache_stats':
                    st.session_state[key] = {}
                elif key == 'erros_form':
                    st.session_state[key] = {}
                else:
                    del st.session_state[key]
        
        logger.info(f"Estado resetado para: {keys}")
    
    def save_backup(self) -> Dict[str, Any]:
        """Salvar backup do estado atual."""
        return {k: st.session_state.get(k) for k in self._state_keys}
    
    def restore_backup(self, backup: Dict[str, Any]) -> None:
        """Restaurar estado a partir de backup."""
        for key, value in backup.items():
            st.session_state[key] = value
        logger.info("Estado restaurado a partir de backup")

class RateLimiter:
    """Implementa rate limiting para prevenir abuso."""
    
    @staticmethod
    def check_limit(key: str, limit: int = 5, window: int = 60) -> Tuple[bool, str]:
        """Verificar se requisição está dentro dos limites."""
        current_time = time.time()
        rate_key = f"rate_{key}"
        
        if rate_key not in st.session_state.rate_limits:
            st.session_state.rate_limits[rate_key] = []
        
        # Remover requisições antigas
        st.session_state.rate_limits[rate_key] = [
            t for t in st.session_state.rate_limits[rate_key]
            if current_time - t < window
        ]
        
        if len(st.session_state.rate_limits[rate_key]) >= limit:
            remaining = window - (current_time - st.session_state.rate_limits[rate_key][0])
            return False, f"Muitas requisições. Aguarde {int(remaining)} segundos."
        
        st.session_state.rate_limits[rate_key].append(current_time)
        return True, "OK"

class DataManager:
    """Gerenciador de dados e cache."""
    
    def __init__(self):
        self.cache_time = {}
        logger.info("DataManager inicializado")
    
    @st.cache_data(ttl=60, show_spinner=False)
    def carregar_dados(_conn: GSheetsConnection, force_refresh: bool = False) -> pd.DataFrame:
        """Carregar dados do Google Sheets com cache otimizado."""
        try:
            if force_refresh:
                st.cache_data.clear()
                logger.info("Cache limpo para recarregamento forçado")
            
            logger.info("Carregando dados do Google Sheets...")
            df = _conn.read(worksheet="Página1")
            
            if df.empty:
                logger.warning("DataFrame vazio retornado do Google Sheets")
                return pd.DataFrame()
            
            # Otimizar tipos de dados
            column_types = {
                'Data': 'datetime64[ns]',
                'Timestamp': 'datetime64[ns]',
                'Preço': 'float64',
                'Status': 'category'
            }
            
            for col, dtype in column_types.items():
                if col in df.columns:
                    try:
                        if col == 'Data':
                            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
                        elif col == 'Timestamp':
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                        else:
                            df[col] = df[col].astype(dtype)
                    except Exception as e:
                        logger.warning(f"Erro ao converter coluna {col}: {e}")
            
            logger.info(f"Dados carregados: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}", exc_info=True)
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
            return pd.DataFrame()
    
    def get_estatisticas(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular estatísticas em cache."""
        if df.empty:
            return {
                'total': 0,
                'pendentes': 0,
                'confirmados': 0,
                'cancelados': 0,
                'recente': None,
                'receita_total': 0,
                'receita_mensal': 0
            }
        
        cache_key = f"stats_{hash(str(df.shape))}"
        current_time = time.time()
        
        # Verificar cache (30 segundos)
        if (cache_key in st.session_state.cache_stats and 
            current_time - self.cache_time.get(cache_key, 0) < 30):
            logger.debug(f"Estatísticas retornadas do cache: {cache_key}")
            return st.session_state.cache_stats[cache_key]
        
        try:
            # Calcular estatísticas
            total = len(df)
            pendentes = len(df[df['Status'] == 'Pendente'])
            confirmados = len(df[df['Status'] == 'Confirmado'])
            cancelados = len(df[df['Status'] == 'Cancelado'])
            
            # Calcular receitas
            receita_total = 0
            receita_mensal = 0
            
            if 'Preço' in df.columns and 'Status' in df.columns:
                receita_total = df[df['Status'] == 'Confirmado']['Preço'].sum()
                
                # Receita do mês atual
                current_month = datetime.now().month
                current_year = datetime.now().year
                df['Month'] = pd.to_datetime(df['Timestamp']).dt.month
                df['Year'] = pd.to_datetime(df['Timestamp']).dt.year
                receita_mensal = df[
                    (df['Status'] == 'Confirmado') & 
                    (df['Month'] == current_month) & 
                    (df['Year'] == current_year)
                ]['Preço'].sum()
            
            stats = {
                'total': total,
                'pendentes': pendentes,
                'confirmados': confirmados,
                'cancelados': cancelados,
                'recente': df['Timestamp'].max() if 'Timestamp' in df.columns else None,
                'receita_total': receita_total,
                'receita_mensal': receita_mensal,
                'taxa_conversao': confirmados / total if total > 0 else 0
            }
            
            # Atualizar cache
            st.session_state.cache_stats[cache_key] = stats
            self.cache_time[cache_key] = current_time
            
            logger.info(f"Estatísticas calculadas: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}", exc_info=True)
            return {}

# ============================================
# 3. MODELOS DE DADOS (Pydantic)
# ============================================

class ReservaModel(BaseModel):
    """Modelo de validação para reservas."""
    aluno: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    servico: str
    unidade: str
    data: str
    horario: str
    telefone: Optional[str] = None
    observacoes: Optional[str] = None
    
    @validator('aluno')
    def validate_nome(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        if not all(c.isalpha() or c.isspace() or c in ".-'" for c in v):
            raise ValueError('Nome deve conter apenas letras, espaços e caracteres especiais permitidos')
        return v.title()
    
    @validator('horario')
    def validate_horario(cls, v):
        try:
            hora = int(v.split(':')[0])
            if hora < 7 or hora > 22:
                raise ValueError('Horário deve ser entre 07:00 e 22:00')
            if v not in [f"{h:02d}:00" for h in range(7, 23)]:
                raise ValueError('Horário deve ser em ponto (ex: 08:00, 09:00)')
        except (ValueError, IndexError):
            raise ValueError('Horário inválido. Use formato HH:00')
        return v
    
    @validator('data')
    def validate_data(cls, v):
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError('Data inválida. Use formato DD/MM/YYYY')
        
        # Verificar se não é no passado
        data_obj = datetime.strptime(v, '%d/%m/%Y').date()
        if data_obj < date.today():
            raise ValueError('Data não pode ser no passado')
        
        return v

class ContatoModel(BaseModel):
    """Modelo de validação para contato."""
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    mensagem: str = Field(..., min_length=10, max_length=1000)
    telefone: Optional[str] = None
    
    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            v = re.sub(r'\D', '', v)
            if len(v) < 10 or len(v) > 11:
                raise ValueError('Telefone inválido')
        return v

# ============================================
# 4. CONSTANTES E CONFIGURAÇÕES
# ============================================

# Senhas e configurações sensíveis
try:
    SENHA_ADMIN = os.getenv("ADMIN_PASSWORD", st.secrets.get("ADMIN_PASSWORD", "tennispro2024"))
except:
    SENHA_ADMIN = "tennispro2024"

# Serviços disponíveis
SERVICOS = {
    "particular": {
        "nome": "Aula particular", 
        "preco": 250, 
        "icone": "🎾",
        "descricao": "Aula individual com foco total no aluno",
        "duracao": "1 hora",
        "categoria": "Aulas"
    },
    "grupo": {
        "nome": "Aula em grupo", 
        "preco": 200, 
        "icone": "👥",
        "descricao": "Aula em grupo de até 4 pessoas",
        "duracao": "1 hora",
        "categoria": "Aulas"
    },
    "kids": {
        "nome": "Aula Kids", 
        "preco": 200, 
        "icone": "👶",
        "descricao": "Aula especializada para crianças",
        "duracao": "1 hora",
        "categoria": "Aulas"
    },
    "personal": {
        "nome": "Personal trainer", 
        "preco": 250, 
        "icone": "💪",
        "descricao": "Treinamento personalizado",
        "duracao": "1 hora",
        "categoria": "Treinamento"
    },
    "competitivo": {
        "nome": "Treinamento competitivo", 
        "preco": 1400, 
        "icone": "🏆",
        "descricao": "Pacote mensal para competidores",
        "duracao": "8 horas/mês",
        "categoria": "Treinamento"
    },
    "eventos": {
        "nome": "Eventos", 
        "preco": 0, 
        "icone": "🎉",
        "descricao": "Organização de eventos especiais",
        "duracao": "Variável",
        "categoria": "Especial"
    }
}

# Academias parceiras
ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488",
        "lat": -23.5878,
        "lng": -46.6578,
        "horarios": "6:00 às 22:00",
        "quadras": 8,
        "cobertura": "Sim"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828",
        "lat": -23.6035,
        "lng": -46.6653,
        "horarios": "7:00 às 23:00",
        "quadras": 6,
        "cobertura": "Não"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028",
        "lat": -23.6187,
        "lng": -46.6698,
        "horarios": "6:30 às 22:30",
        "quadras": 10,
        "cobertura": "Sim"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860",
        "lat": -23.6354,
        "lng": -46.7279,
        "horarios": "5:00 às 24:00",
        "quadras": 12,
        "cobertura": "Sim"
    }
}

# Links dos formulários
FORM_LINKS = {
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform",
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform"
}

# Constantes de tempo
TEMPO_PAGAMENTO = 300  # 5 minutos em segundos
TEMPO_CACHE = 60       # 1 minuto para cache

# ============================================
# 5. COMPONENTES REUTILIZÁVEIS
# ============================================

def tennis_card(title: str, content: str, icon: str = "🎾", color: str = "default") -> None:
    """Componente de card com tema de tênis."""
    colors = {
        "default": "#FFD700",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "info": "#2196F3",
        "error": "#F44336"
    }
    
    border_color = colors.get(color, colors["default"])
    
    st.markdown(f"""
    <div class="tennis-card" style="border-left: 5px solid {border_color};">
        <div class="tennis-card-header">
            <span class="tennis-ball-icon" style="color: {border_color};">{icon}</span>
            <h3 style="margin: 0; color: #333;">{title}</h3>
        </div>
        <div class="tennis-card-body">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def timer_component(seconds: int, key: str) -> Tuple[bool, str]:
    """Componente de timer reutilizável."""
    if key not in st.session_state:
        st.session_state[key] = time.time()
    
    elapsed = time.time() - st.session_state[key]
    remaining = max(0, seconds - int(elapsed))
    
    if remaining <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(remaining, 60)
    
    # Cor baseada no tempo restante
    if remaining < 60:
        color = "#F44336"  # Vermelho
    elif remaining < 120:
        color = "#FF9800"  # Laranja
    else:
        color = "#4CAF50"  # Verde
    
    return True, f'<span style="color: {color}; font-weight: bold;">⏱️ {m:02d}:{s:02d}</span>'

def loading_spinner(text: str = "Carregando...") -> None:
    """Componente de loading animado."""
    st.markdown(f"""
    <div style="text-align: center; padding: 30px;">
        <div class="loading-spinner"></div>
        <p style="margin-top: 15px; color: #666;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

def success_message(message: str) -> None:
    """Exibe mensagem de sucesso."""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def error_message(message: str) -> None:
    """Exibe mensagem de erro."""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)

def warning_message(message: str) -> None:
    """Exibe mensagem de alerta."""
    st.markdown(f"""
    <div class="warning-message">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 6. FUNÇÕES DE VALIDAÇÃO E UTILITÁRIAS
# ============================================

def validar_reserva_completa(dados: Dict[str, Any]) -> Tuple[bool, str]:
    """Validação completa dos dados da reserva usando Pydantic."""
    try:
        ReservaModel(**dados)
        return True, "Validação bem-sucedida"
    except Exception as e:
        logger.warning(f"Validação falhou: {str(e)}")
        return False, str(e)

def validar_telefone(telefone: str) -> bool:
    """Valida formato de telefone brasileiro."""
    telefone_limpo = re.sub(r'\D', '', telefone)
    return len(telefone_limpo) in [10, 11] and telefone_limpo[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']

def formatar_moeda(valor: float) -> str:
    """Formata valor em moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_idade(data_nascimento: date) -> int:
    """Calcula idade a partir da data de nascimento."""
    hoje = date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

def enviar_email_confirmacao(email: str, reserva: Dict[str, Any]) -> bool:
    """Simula envio de e-mail de confirmação."""
    try:
        logger.info(f"E-mail de confirmação enviado para: {email}")
        logger.info(f"Detalhes da reserva: {reserva}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        return False

def log_reserva(reserva: Dict[str, Any], success: bool, user_ip: str = "N/A") -> None:
    """Log detalhado de reservas."""
    if success:
        logger.info(f"RESERVA CONFIRMADA - Aluno: {reserva.get('Aluno')}, "
                   f"Email: {reserva.get('E-mail')}, IP: {user_ip}")
    else:
        logger.error(f"FALHA NA RESERVA - Dados: {reserva}, IP: {user_ip}")

# ============================================
# 7. CSS GLOBAL AVANÇADO
# ============================================

st.markdown("""
<style>
    /* Fundo e container principal */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.9)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    /* Container principal */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Títulos */
    .header-title { 
        color: white; 
        font-size: 48px; 
        font-weight: 800; 
        text-align: center; 
        margin: 20px 0 30px; 
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5); 
        letter-spacing: 1px;
    }
    
    .section-title {
        color: #FFD700;
        font-size: 28px;
        font-weight: 700;
        margin: 25px 0 15px;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 8px;
    }
    
    /* Cards */
    .custom-card { 
        background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.95)); 
        padding: 35px; 
        border-radius: 20px; 
        color: #333; 
        margin: 0 auto 30px;
        max-width: 1000px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.25);
        border: 1px solid rgba(255, 215, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .custom-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FFD700, #FFA500);
    }
    
    .tennis-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .tennis-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .tennis-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    
    .tennis-ball-icon {
        font-size: 28px;
        margin-right: 15px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    /* Links e botões */
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: all 0.3s ease; 
        display: block; 
        padding: 25px; 
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(0,0,0,0.4), rgba(0,0,0,0.6));
        margin: 15px 0;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
    }
    
    .clean-link:hover { 
        transform: translateY(-8px) scale(1.02); 
        color: #FFD700 !important; 
        background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,0,0,0.8));
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border-color: #FFD700;
    }
    
    .icon-text { 
        font-size: 55px;
        margin-bottom: 15px; 
        transition: transform 0.3s ease;
    }
    
    .clean-link:hover .icon-text {
        transform: scale(1.15) rotate(10deg);
    }
    
    .label-text { 
        font-size: 20px; 
        font-weight: 700; 
        letter-spacing: 1px; 
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    
    .link-description {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.4;
        margin-top: 10px;
        max-width: 90%;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        color: #000 !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4) !important;
        background: linear-gradient(135deg, #FFA500, #FFD700) !important;
    }
    
    /* WhatsApp flutuante */
    .whatsapp-float { 
        position: fixed; 
        width: 65px; 
        height: 65px; 
        bottom: 40px; 
        right: 40px; 
        background: linear-gradient(135deg, #25d366, #128C7E); 
        color: #FFF; 
        border-radius: 50%; 
        text-align: center; 
        font-size: 40px; 
        box-shadow: 0 8px 25px rgba(37, 211, 102, 0.4); 
        z-index: 9999; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-decoration: none; 
        transition: all 0.3s ease;
        animation: pulse-whatsapp 2s infinite;
    }
    
    @keyframes pulse-whatsapp {
        0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    
    .whatsapp-float:hover {
        transform: scale(1.1) rotate(10deg);
        box-shadow: 0 12px 30px rgba(37, 211, 102, 0.6);
    }
    
    /* Assinatura */
    .assinatura-footer { 
        position: fixed; 
        bottom: 20px; 
        left: 20px; 
        width: 140px; 
        z-index: 9998; 
        opacity: 0.9;
        transition: opacity 0.3s ease;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    
    .assinatura-footer:hover {
        opacity: 1;
        transform: scale(1.05);
    }
    
    /* Sidebar */
    .sidebar-detalhe { 
        font-size: 12px; 
        color: #ddd; 
        margin-bottom: 12px; 
        line-height: 1.4; 
        padding-left: 10px;
        border-left: 2px solid #FFD700;
    }
    
    /* Mensagens */
    .error-message {
        color: #f44336;
        font-size: 14px;
        margin: 10px 0;
        padding: 12px 15px;
        border-radius: 8px;
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
        animation: shake 0.5s ease;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .success-message {
        color: #4CAF50;
        font-size: 14px;
        margin: 10px 0;
        padding: 12px 15px;
        border-radius: 8px;
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        animation: fadeIn 0.5s ease;
    }
    
    .warning-message {
        color: #FF9800;
        font-size: 14px;
        margin: 10px 0;
        padding: 12px 15px;
        border-radius: 8px;
        background: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #FF9800;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Timer */
    .timer-warning {
        color: #FF9800;
        font-weight: 700;
        font-size: 18px;
        text-align: center;
        padding: 15px;
        border: 2px solid #FF9800;
        border-radius: 12px;
        background: rgba(255, 152, 0, 0.1);
        animation: pulse 2s infinite;
        margin: 20px 0;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 152, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0); }
    }
    
    /* Bola de tênis amarela */
    .tennis-ball-yellow {
        color: #FFD700 !important;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.8), 0 0 25px rgba(255, 215, 0, 0.5) !important;
        filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.7));
        animation: glow 1.5s ease-in-out infinite alternate;
        display: inline-block;
    }
    
    @keyframes glow {
        from {
            text-shadow: 0 0 10px #FFD700, 0 0 20px #FFD700;
        }
        to {
            text-shadow: 0 0 20px #FFD700, 0 0 30px #FFD700, 0 0 40px #FFD700;
        }
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: inline-block;
        width: 40px
