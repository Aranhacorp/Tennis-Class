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
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple
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
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    file_handler = RotatingFileHandler(
        'tennis_class.log',
        maxBytes=1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    initial_sidebar_state="expanded"
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

class RateLimiter:
    """Implementa rate limiting para prevenir abuso."""
    
    @staticmethod
    def check_limit(key: str, limit: int = 5, window: int = 60) -> Tuple[bool, str]:
        """Verificar se requisição está dentro dos limites."""
        current_time = time.time()
        rate_key = f"rate_{key}"
        
        if rate_key not in st.session_state.rate_limits:
            st.session_state.rate_limits[rate_key] = []
        
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
    
    @st.cache_data(ttl=60, show_spinner=False)
    def carregar_dados(_conn: GSheetsConnection, force_refresh: bool = False) -> pd.DataFrame:
        """Carregar dados do Google Sheets com cache otimizado."""
        try:
            if force_refresh:
                st.cache_data.clear()
            
            df = _conn.read(worksheet="Página1")
            
            if df.empty:
                return pd.DataFrame()
            
            # Converter tipos de dados
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            if 'Timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
            return pd.DataFrame()

# ============================================
# 3. MODELOS DE DADOS
# ============================================

class ReservaModel(BaseModel):
    """Modelo de validação para reservas."""
    aluno: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    servico: str
    unidade: str
    data: str
    horario: str
    
    @validator('aluno')
    def validate_nome(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        return v.title()
    
    @validator('horario')
    def validate_horario(cls, v):
        try:
            hora = int(v.split(':')[0])
            if hora < 7 or hora > 22:
                raise ValueError('Horário deve ser entre 07:00 e 22:00')
        except:
            raise ValueError('Horário inválido')
        return v
    
    @validator('data')
    def validate_data(cls, v):
        try:
            datetime.strptime(v, '%d/%m/%Y')
            data_obj = datetime.strptime(v, '%d/%m/%Y').date()
            if data_obj < date.today():
                raise ValueError('Data não pode ser no passado')
        except ValueError:
            raise ValueError('Data inválida. Use formato DD/MM/YYYY')
        return v

# ============================================
# 4. CONSTANTES
# ============================================

# Senha admin
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
        "descricao": "Aula individual"
    },
    "grupo": {
        "nome": "Aula em grupo", 
        "preco": 200, 
        "icone": "👥",
        "descricao": "Aula em grupo"
    },
    "kids": {
        "nome": "Aula Kids", 
        "preco": 200, 
        "icone": "👶",
        "descricao": "Para crianças"
    },
    "personal": {
        "nome": "Personal trainer", 
        "preco": 250, 
        "icone": "💪",
        "descricao": "Treinamento"
    },
    "competitivo": {
        "nome": "Treinamento competitivo", 
        "preco": 1400, 
        "icone": "🏆",
        "descricao": "Pacote mensal"
    },
    "eventos": {
        "nome": "Eventos", 
        "preco": 0, 
        "icone": "🎉",
        "descricao": "Eventos especiais"
    }
}

# Academias
ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860"
    }
}

# Links
FORM_LINKS = {
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform",
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform"
}

TEMPO_PAGAMENTO = 300  # 5 minutos

# ============================================
# 5. CSS GLOBAL (SIMPLIFICADO)
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }
    .header-title { 
        color: white; 
        font-size: 50px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
        text-shadow: 2px 2px 4px black; 
    }
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
        position: relative; 
        margin: 0 auto;
        max-width: 1000px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: all 0.3s ease; 
        display: block; 
        padding: 20px; 
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.3);
        margin: 10px 0;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .clean-link:hover { 
        transform: translateY(-5px); 
        color: #4CAF50 !important; 
        background-color: rgba(0, 0, 0, 0.5);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border-color: #4CAF50;
    }
    .icon-text { 
        font-size: 50px;
        margin-bottom: 10px; 
    }
    .label-text { 
        font-size: 18px; 
        font-weight: bold; 
        letter-spacing: 1px; 
        margin-bottom: 8px;
    }
    .whatsapp-float { 
        position: fixed; 
        width: 60px; 
        height: 60px; 
        bottom: 40px; 
        right: 40px; 
        background-color: #25d366; 
        color: #FFF; 
        border-radius: 50px; 
        text-align: center; 
        font-size: 35px; 
        box-shadow: 2px 2px 3px #999; 
        z-index: 9999; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-decoration: none; 
        transition: all 0.3s ease;
    }
    .whatsapp-float:hover {
        transform: scale(1.1);
    }
    .assinatura-footer { 
        position: fixed; 
        bottom: 15px; 
        left: 20px; 
        width: 130px; 
        z-index: 9999; 
        opacity: 0.8;
    }
    .sidebar-detalhe { 
        font-size: 11px; 
        color: #ccc; 
        margin-bottom: 10px; 
        line-height: 1.2; 
    }
    .error-message {
        color: #ff4444;
        font-size: 14px;
        margin-top: 5px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(255, 68, 68, 0.1);
        border-left: 4px solid #ff4444;
    }
    .success-message {
        color: #00C851;
        font-size: 14px;
        margin-top: 5px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(0, 200, 81, 0.1);
        border-left: 4px solid #00C851;
    }
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        padding: 12px;
        border: 2px solid #ff8800;
        border-radius: 10px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    .tennis-ball-yellow {
        color: #FFFF00 !important;
        text-shadow: 0 0 10px #FF0;
    }
    .stButton > button {
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Elementos HTML flutuantes
st.markdown("""
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="WhatsApp">
</a>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura">
""", unsafe_allow_html=True)

# ============================================
# 6. INICIALIZAÇÃO DOS GERENCIADORES
# ============================================

state_manager = StateManager()
rate_limiter = RateLimiter()
data_manager = DataManager()

# ============================================
# 7. FUNÇÕES AUXILIARES
# ============================================

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_nome(nome: str) -> bool:
    """Valida nome."""
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    return True

def salvar_reserva(reserva: Dict[str, Any]) -> bool:
    """Salva uma reserva no Google Sheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = data_manager.carregar_dados()
        
        reserva["ID"] = str(uuid.uuid4())[:8]
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Pendente"
        
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        st.cache_data.clear()
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        return False

def mostrar_timer(tempo_total: int, inicio_time: float) -> tuple[bool, str]:
    """Calcula e formata o tempo restante."""
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

# ============================================
# 8. MENU LATERAL
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: #FFFF00; text-align: center;'>🎾 MENU</h2>", 
                unsafe_allow_html=True)
    
    menu_items = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    
    for item in menu_items:
        if st.button(f"🎾 {item}", key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: #FFFF00;'>🎾 ACADEMIAS</h3>", 
                unsafe_allow_html=True)
    
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"📍 **{nome}**\n"
            f"<div class='sidebar-detalhe'>"
            f"{info['endereco']}<br>📞 {info['telefone']}"
            f"</div>", 
            unsafe_allow_html=True
        )

# ============================================
# 9. TÍTULO PRINCIPAL
# ============================================

st.markdown('<div class="header-title"><span class="tennis-ball-yellow">🎾</span> TENNIS CLASS</div>', 
            unsafe_allow_html=True)

# ============================================
# 10. LÓGICA DAS PÁGINAS
# ============================================

# PÁGINA: HOME
if st.session_state.pagina == "Home" or st.session_state.pagina is None:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.markdown('<h3 style="text-align: center; color: #333;">🎾 Agendar Aula</h3>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input(
                    "Nome do Aluno *",
                    placeholder="Ex: João Silva"
                )
            with col2:
                email = st.text_input(
                    "E-mail *",
                    placeholder="Ex: joao.silva@email.com"
                )
            
            # Lista de serviços
            servicos_lista = [
                f"{SERVICOS[key]['icone']} {SERVICOS[key]['nome']} R$ {SERVICOS[key]['preco']}"
                f"{'/hora' if key != 'competitivo' else '/mês'}"
                for key in SERVICOS.keys()
            ]
            
            col3, col4 = st.columns(2)
            with col3:
                servico = st.selectbox("Serviço *", servicos_lista)
            with col4:
                unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            col5, col6 = st.columns(2)
            with col5:
                dt = st.date_input("Data *", format="DD/MM/YYYY")
            with col6:
                hr = st.selectbox("Horário *", [f"{h:02d}:00" for h in range(7, 23)])
            
            submit = st.form_submit_button(
                "🎾 AVANÇAR PARA PAGAMENTO", 
                use_container_width=True,
                type="primary"
            )
            
            if submit:
                st.session_state.erros_form = {}
                
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido."
                
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido."
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": dt.strftime("%d/%m/%Y"),
                        "Horário": hr,
                        "Aluno": aluno.strip(),
                        "Serviço": servico,
                        "Unidade": unidade,
                        "E-mail": email.lower().strip()
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', 
                                  unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        
        # QR Code
        st.image(
            "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
            width=250
        )
        
        # Chave PIX
        st.markdown("""
        <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <p style="text-align: center; font-family: monospace; font-size: 18px; margin: 0;">
                <strong>aranha.corp@gmail.com</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Timer
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(
                TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                st.markdown(
                    f'<div class="timer-warning">{mensagem_timer}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.session_state.pagamento_ativo = False
                st.warning("⏰ Tempo esgotado!")
                st.rerun()
        
        # Botão de confirmação
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎾 CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
                if salvar_reserva(st.session_state.reserva_temp):
                    st.balloons()
                    st.markdown(
                        '<div class="success-message">'
                        '✅ Reserva confirmada!'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    st.session_state.pagamento_ativo = False
                    st.session_state.reserva_temp = {}
                    time.sleep(2)
                    st.rerun()
    
    # Link do regulamento
    st.markdown("""
    <hr style="margin: 30px 0;">
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit" 
       target="_blank" 
       style="display: block; text-align: center; text-decoration: none; color: #555;">
        📄 Ler Regulamento
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: PREÇOS
elif st.session_state.pagina == "Preços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Tabela de Preços</h3>', 
               unsafe_allow_html=True)
    st.markdown("---")
    
    for key, info in SERVICOS.items():
        if key == "eventos":
            st.markdown(f"<div>🎾 <strong>{info['nome']}:</strong> <em>Valor a combinar</em></div>")
        else:
            unidade = "/hora" if key != "competitivo" else "/mês"
            st.markdown(f"<div>🎾 <strong>{info['nome']}:</strong> R$ {info['preco']} {unidade}</div>")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Portal de Cadastros</h3>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">🎾</div>
            <div class="label-text">PROFESSOR</div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: DASHBOARD
elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.admin_autenticado:
        st.markdown('<h3 style="text-align: center; color: #333;">🎾 Acesso Administrativo</h3>', 
                   unsafe_allow_html=True)
        
        senha = st.text_input(
            "Digite a senha de administrador:", 
            type="password"
        )
        
        if st.button("🔓 Acessar", use_container_width=True):
            if senha == SENHA_ADMIN:
                st.session_state.admin_autenticado = True
                st.success("✅ Acesso concedido!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
        
        if st.button("🔙 Voltar para Home", use_container_width=True):
            st.session_state.pagina = "Home"
            st.rerun()
    
    else:
        st.markdown('<h3 style="text-align: center; color: #333;">🎾 Dashboard - Reservas</h3>', 
                   unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()
        
        st.markdown("---")
        
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = data_manager.carregar_dados()
            
            if not df.empty:
                # Métricas
                total = len(df)
                pendentes = len(df[df['Status'] == 'Pendente'])
                confirmados = len(df[df['Status'] == 'Confirmado'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total)
                with col2:
                    st.metric("Pendentes", pendentes)
                with col3:
                    st.metric("Confirmados", confirmados)
                
                st.markdown("---")
                
                # Tabela
                st.dataframe(
                    df.sort_values('Data', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Botões
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.rerun()
                
                with col2:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar CSV",
                        data=csv,
                        file_name=f"reservas_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("📭 Nenhuma reserva encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Canais de Atendimento</h3>', 
               unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 E-mail")
        st.markdown("""
        <div style='padding: 20px; background: #f5f5f5; border-radius: 10px;'>
            <strong>aranha.corp@gmail.com</strong><br>
            <span style="font-size: 13px;">Respondemos em até 24h</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown("""
        <div style='padding: 20px; background: #f5f5f5; border-radius: 10px;'>
            <strong>(11) 97142-5028</strong><br>
            <span style="font-size: 13px;">Atendimento direto</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 11. RODAPÉ
# ============================================

st.markdown("""
<div style="text-align: center; color: #666; margin-top: 50px; padding: 20px;">
    <hr style="border: none; border-top: 1px solid #444; margin: 20px 0;">
    <p>Tennis Class &copy; 2024 - Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
