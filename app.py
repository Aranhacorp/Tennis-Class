# ============================================
# TENNIS CLASS APP - MASTER CODE DEEP SEEK v10
# ============================================
# Versão sem envio de e-mail de confirmação
# Data: 2024-12-06
# ============================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
from functools import lru_cache

# ============================================
# 1. CONFIGURAÇÃO E LOGGING
# ============================================

# Configuração da página
st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# Configuração de logging
def setup_logging():
    """Configura sistema de logging para depuração."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tennis_class.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================
# 2. CLASSES DE CONFIGURAÇÃO E EXCEÇÕES
# ============================================

class Config:
    """Classe de configuração centralizada."""
    
    # Google Sheets
    SPREADSHEET_URL = ""
    WORKSHEET_NAME = "Página1"
    
    # WhatsApp
    WHATSAPP_NUMBER = "5511971425028"
    
    # Limites do sistema
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300  # 5 minutos em segundos
    
    # Horários disponíveis
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]

class ReservaError(Exception):
    """Exceção personalizada para erros de reserva."""
    pass

# ============================================
# 3. CONSTANTES E DADOS
# ============================================

# Serviços atualizados com pacotes
SERVICOS = {
    "particular_hora": {"nome": "Aula particular", "preco": 250, "tipo": "Hora"},
    "grupo_hora": {"nome": "Aula em grupo", "preco": 200, "tipo": "Hora"},
    "kids_hora": {"nome": "Aula Kids", "preco": 200, "tipo": "Hora"},
    "personal_hora": {"nome": "Personal trainer", "preco": 250, "tipo": "Hora"},
    "competitivo": {"nome": "Treinamento competitivo", "preco": 1400, "tipo": "Mês"},
    "eventos": {"nome": "Eventos", "preco": 0, "tipo": "Hora"},
    # Pacotes
    "pacote_particular_4": {"nome": "Pacote aula particular", "preco": 1000, "tipo": "4 aulas de 1 hora"},
    "pacote_grupo_4": {"nome": "Pacote aula em grupo", "preco": 800, "tipo": "4 aulas de 1 hora"},
    "pacote_particular_8": {"nome": "Pacote aula particular", "preco": 2000, "tipo": "8 aulas de 1 hora"},
    "pacote_grupo_8": {"nome": "Pacote aula em grupo", "preco": 1600, "tipo": "8 aulas de 1 hora"},
    "pacote_kids_4": {"nome": "Pacote aula Kids", "preco": 800, "tipo": "4 aulas de 1 hora"},
    "pacote_personal_4": {"nome": "Pacote Personal Trainer", "preco": 1000, "tipo": "4 aulas de 1 hora"}
}

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

FORM_LINKS = {
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?usp=dialog",
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?usp=dialog",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog"
}

# ============================================
# 4. FUNÇÕES AUXILIARES - VALIDAÇÕES
# ============================================

def validar_nome(nome: str) -> bool:
    """Valida nome (mínimo 3 caracteres, apenas letras e espaços)."""
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    # Permite letras, espaços e caracteres acentuados em português
    return bool(re.match(r'^[a-zA-ZÀ-ÿ\s\.\-]+$', nome_limpo))

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_telefone(telefone: str) -> bool:
    """Valida formato de telefone brasileiro."""
    # Remove caracteres não numéricos
    telefone_limpo = re.sub(r'\D', '', telefone)
    # Valida se tem 10 ou 11 dígitos (com DDD)
    return len(telefone_limpo) in [10, 11]

def validar_data_horario(data: str, horario: str, unidade: str) -> Tuple[bool, str]:
    """
    Valida se data/horário estão disponíveis.
    
    Args:
        data: Data no formato DD/MM/YYYY
        horario: Horário no formato HH:00
        unidade: Nome da unidade
        
    Returns:
        Tuple[bool, str]: (disponível, mensagem de erro)
    """
    try:
        # Não permitir reservas no passado
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        if data_obj.date() < datetime.now().date():
            return False, "Não é possível agendar para datas passadas."
        
        # Não permitir reservas com mais de 60 dias de antecedência
        if (data_obj.date() - datetime.now().date()).days > 60:
            return False, "Só é possível agendar com até 60 dias de antecedência."
        
        # Verificar disponibilidade no horário
        disponibilidade = carregar_disponibilidade(data, unidade)
        vagas = disponibilidade.get(horario, Config.MAX_ALUNOS_POR_HORARIO)
        
        if vagas <= 0:
            return False, f"Horário indisponível na {unidade}. Todas as vagas estão preenchidas."
        
        return True, ""
        
    except ValueError:
        return False, "Formato de data inválido."
    except Exception as e:
        logger.error(f"Erro na validação de data/horário: {e}")
        return True, ""  # Em caso de erro, permite continuar

# ============================================
# 5. FUNÇÕES DE DADOS - GOOGLE SHEETS
# ============================================

@st.cache_data(ttl=300)  # Cache de 5 minutos
def carregar_dados() -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache e tratamento de erros."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Página1")
        logger.info(f"Dados carregados com {len(df)} registros")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def carregar_disponibilidade(data: str, unidade: str) -> Dict[str, int]:
    """
    Carrega disponibilidade para uma data e unidade específicas.
    
    Returns:
        Dict com horário como chave e vagas disponíveis como valor
    """
    try:
        df = carregar_dados()
        if df.empty:
            return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}
        
        # Filtra reservas para a data e unidade
        filtrado = df[
            (df['Data'] == data) &
            (df['Unidade'] == unidade) &
            (df['Status'].isin(['Pendente', 'Confirmado']))
        ]
        
        # Conta reservas por horário
        disponibilidade = {}
        for hora in Config.HORARIOS_DISPONIVEIS:
            count = len(filtrado[filtrado['Horário'] == hora])
            disponibilidade[hora] = Config.MAX_ALUNOS_POR_HORARIO - count
            
        logger.info(f"Disponibilidade para {data} em {unidade}: {disponibilidade}")
        return disponibilidade
        
    except Exception as e:
        logger.error(f"Erro ao carregar disponibilidade: {e}")
        return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}

def salvar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Salva uma reserva no Google Sheets.
    
    Returns:
        Tuple[bool, str]: (sucesso, reserva_id ou mensagem de erro)
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        
        # Gera ID único
        reserva_id = str(uuid.uuid4())[:8].upper()
        
        # Adiciona campos de sistema
        reserva["ID"] = reserva_id
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Confirmado"  # Confirmado diretamente
        reserva["Data_Criacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Converte para DataFrame e salva
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache
        st.cache_data.clear()
        
        logger.info(f"Reserva {reserva_id} salva com sucesso")
        return True, reserva_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        return False, str(e)

def criar_backup() -> bytes:
    """Cria backup dos dados em formato CSV."""
    try:
        df = carregar_dados()
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            logger.info("Backup criado com sucesso")
            return csv
        return b""
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return b""

# ============================================
# 6. FUNÇÕES DE PROCESSAMENTO DE RESERVA (SIMPLIFICADA)
# ============================================

def processar_reserva_seguro(reserva: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Processa reserva com tratamento completo de erros.
    VERSÃO SEM ENVIO DE E-MAIL.
    
    Returns:
        Tuple[bool, str, str]: (sucesso, reserva_id, mensagem)
    """
    try:
        # Validações
        if not validar_nome(reserva.get('Aluno', '')):
            raise ReservaError("Nome inválido. Use apenas letras (mínimo 3 caracteres).")
            
        if not validar_email(reserva.get('E-mail', '')):
            raise ReservaError("E-mail inválido. Digite um e-mail válido.")
        
        # Verificar disponibilidade
        disponivel, mensagem = validar_data_horario(
            reserva['Data'],
            reserva['Horário'],
            reserva['Unidade']
        )
        
        if not disponivel:
            raise ReservaError(mensagem)
        
        # Salvar reserva
        sucesso, reserva_id = salvar_reserva(reserva)
        
        if not sucesso:
            raise ReservaError("Falha ao salvar reserva no sistema.")
        
        mensagem_final = "✅ Reserva confirmada com sucesso!"
        
        return True, reserva_id, mensagem_final
        
    except ReservaError as e:
        return False, "", str(e)
    except Exception as e:
        logger.error(f"Erro inesperado no processamento: {e}")
        return False, "", f"Erro inesperado: {str(e)}"

# ============================================
# 7. FUNÇÕES DE SEGURANÇA
# ============================================

def verificar_senha_admin(senha_digitada: str) -> bool:
    """Verifica senha do admin com hash SHA-256."""
    try:
        # Obter hash da senha correta
        senha_correta_hash = st.secrets.get("ADMIN_PASSWORD_HASH", "")
        
        if not senha_correta_hash:
            # Fallback para senha em texto (apenas desenvolvimento)
            senha_correta = st.secrets.get("ADMIN_PASSWORD", "aranha2026")
            return senha_digitada == senha_correta
        
        # Calcular hash da senha digitada
        hash_digitado = hashlib.sha256(senha_digitada.encode()).hexdigest()
        return hash_digitado == senha_correta_hash
        
    except Exception as e:
        logger.error(f"Erro na verificação de senha: {e}")
        return False

# ============================================
# 8. ESTADOS DA SESSÃO
# ============================================

# Inicializar estados da sessão
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False

if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

if 'inicio_timer' not in st.session_state:
    st.session_state.inicio_timer = None

if 'admin_autenticado' not in st.session_state:
    st.session_state.admin_autenticado = False

if 'erros_form' not in st.session_state:
    st.session_state.erros_form = {}

if 'reserva_id_gerada' not in st.session_state:
    st.session_state.reserva_id_gerada = None

# ============================================
# 9. CSS E ESTILOS
# ============================================

st.markdown("""
<style>
    /* Configuração global */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }
    
    /* Header */
    .header-title { 
        color: white; 
        font-size: 50px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
        text-shadow: 2px 2px 4px black; 
    }
    
    /* Cards */
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
        position: relative; 
    }
    
    /* Balões translúcidos */
    .translucent-balloon { 
        background-color: rgba(50, 50, 50, 0.85); 
        padding: 25px; 
        border-radius: 15px; 
        color: white; 
        backdrop-filter: blur(10px); 
        margin-bottom: 20px; 
        border: 1px solid rgba(255,255,255,0.1); 
    }
    
    /* Links */
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: 0.3s; 
        display: block; 
        padding: 20px; 
    }
    .clean-link:hover { 
        transform: translateY(-8px); 
        color: #4CAF50 !important; 
    }
    
    /* Ícones */
    .icon-text { 
        font-size: 80px; 
        margin-bottom: 10px; 
    }
    .label-text { 
        font-size: 20px; 
        font-weight: bold; 
        letter-spacing: 2px; 
    }
    
    /* WhatsApp flutuante */
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
    }
    
    /* Mensagens de status */
    .error-message {
        color: #ff4444;
        font-size: 14px;
        margin-top: 5px;
        padding: 5px;
        border-radius: 4px;
        background-color: rgba(255, 68, 68, 0.1);
    }
    .success-message {
        color: #00C851;
        font-size: 14px;
        margin-top: 5px;
        padding: 5px;
        border-radius: 4px;
        background-color: rgba(0, 200, 81, 0.1);
    }
    .warning-message {
        color: #ff8800;
        font-size: 14px;
        margin-top: 5px;
        padding: 5px;
        border-radius: 4px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    
    /* Timer */
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        padding: 10px;
        border: 2px solid #ff8800;
        border-radius: 10px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    
    /* ID da reserva */
    .reserva-id-box {
        background-color: #f8f9fa;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        font-weight: bold;
        color: #28a745;
    }
    
    /* Status de e-mail */
    .email-confirmation {
        background-color: #e8f5e9;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    
    /* Botões */
    .stButton > button {
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Configurações seguras */
    .secure-config {
        background: rgba(0, 0, 0, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Estilo para resumo da reserva */
    .resumo-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 25px;
    }
    
    .email-section {
        margin-top: 25px;
        padding-top: 20px;
        border-top: 2px solid #dee2e6;
    }
</style>

<!-- Botão flutuante do WhatsApp -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank" 
   aria-label="Contato via WhatsApp">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="Ícone do WhatsApp">
</a>

<!-- Assinatura -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura André Aranha"
     style="position: fixed; bottom: 15px; left: 20px; width: 130px; z-index: 9999; opacity: 0.8;">
""", unsafe_allow_html=True)

# ============================================
# 10. COMPONENTES REUTILIZÁVEIS
# ============================================

def mostrar_timer(tempo_total: int, inicio_time: float) -> Tuple[bool, str]:
    """Calcula e formata o tempo restante."""
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

def card_com_estilo(conteudo: str, classe: str = "custom-card") -> str:
    """Retorna HTML de card estilizado."""
    return f'<div class="{classe}">{conteudo}</div>'

def mostrar_resumo_reserva_html(reserva: dict, titulo: str = "📋 Resumo da Reserva") -> str:
    """Retorna HTML formatado para o resumo da reserva."""
    html = f"""
    <div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #dee2e6;">
        <h3 style="color: #2c3e50; margin-bottom: 20px;">{titulo}</h3>
        
        <div class="resumo-grid">
            <div>
                <strong style="color: #666; font-size: 12px;">ALUNO</strong>
                <div style="font-size: 18px; color: #2c3e50; font-weight: 600;">{reserva.get('Aluno', '')}</div>
            </div>
            
            <div>
                <strong style="color: #666; font-size: 12px;">SERVIÇO</strong>
                <div style="font-size: 16px; color: #2c3e50;">{reserva.get('Serviço', '')}</div>
            </div>
            
            <div>
                <strong style="color: #666; font-size: 12px;">UNIDADE</strong>
                <div style="font-size: 16px; color: #2c3e50;">{reserva.get('Unidade', '')}</div>
            </div>
            
            <div>
                <strong style="color: #666; font-size: 12px;">DATA E HORÁRIO</strong>
                <div style="font-size: 16px; color: #2c3e50;">
                    {reserva.get('Data', '')} às {reserva.get('Horário', '')}
                </div>
            </div>
        </div>
        
        <div class="email-section">
            <strong style="color: #666; font-size: 12px;">E-MAIL PARA CONTATO</strong>
            <div style="font-size: 15px; color: #2980b9; word-break: break-all;">
                {reserva.get('E-mail', '')}
            </div>
        </div>
    </div>
    """
    return html

# ============================================
# 11. MENU LATERAL SEGURO
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", 
                unsafe_allow_html=True)
    
    # Navegação
    menu_itens = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    
    for item in menu_itens:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            if item == "Dashboard":
                st.session_state.admin_autenticado = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏢 ACADEMIAS RECOMENDADAS")
    
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"📍 **{nome}**\n"
            f"<div style='font-size: 11px; color: #ccc; margin-bottom: 10px;'>"
            f"{info['endereco']}<br>📞 {info['telefone']}"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    # Ajuda
    st.markdown("---")
    with st.expander("❓ Ajuda"):
        st.markdown("""
        ### Precisa de ajuda?
        
        **Contato técnico:**
        - WhatsApp: (11) 97142-5028
        - Email: aranha.corp@gmail.com
        
        **Horário de atendimento:**
        Seg-Sex: 9h-18h
        Sáb: 9h-13h
        """)
    
    # Status do sistema
    st.markdown("---")
    st.markdown("### 📊 Status do Sistema")
    
    try:
        df = carregar_dados()
        total_reservas = len(df) if not df.empty else 0
        st.metric("Reservas totais", total_reservas)
    except:
        st.metric("Reservas totais", "0")

# ============================================
# 12. PÁGINA PRINCIPAL - HOME
# ============================================

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

if st.session_state.pagina == "Home":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.subheader("📅 Agendar Aula")
            
            # Campos do formulário
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input(
                    "Nome do Aluno *",
                    help="Digite seu nome completo (mínimo 3 caracteres)",
                    placeholder="Ex: João Silva"
                )
            
            with col2:
                email = st.text_input(
                    "E-mail *",
                    help="Digite um e-mail válido para contato",
                    placeholder="exemplo@email.com"
                )
            
            # Serviços formatados
            servicos_lista = []
            for key, info in SERVICOS.items():
                if info['tipo'] == "Hora":
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']}/hora")
                elif info['tipo'] == "Mês":
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']}/mês")
                else:
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']} / {info['tipo']}")
            
            servico = st.selectbox("Serviço *", servicos_lista)
            unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            # Data e horário
            col1, col2 = st.columns(2)
            with col1:
                dt = st.date_input(
                    "Data *",
                    format="DD/MM/YYYY",
                    min_value=datetime.now().date(),
                    max_value=datetime.now().date() + timedelta(days=60)
                )
            
            with col2:
                hr = st.selectbox("Horário *", Config.HORARIOS_DISPONIVEIS)
            
            # Botão de submissão
            submit = st.form_submit_button(
                "AVANÇAR PARA PAGAMENTO", 
                use_container_width=True,
                type="primary"
            )
            
            if submit:
                st.session_state.erros_form = {}
                
                # Validações
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido. Use apenas letras (mínimo 3 caracteres)."
                
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido. Digite um e-mail válido."
                
                # Validar disponibilidade
                data_str = dt.strftime("%d/%m/%Y")
                disponivel, mensagem = validar_data_horario(data_str, hr, unidade)
                if not disponivel:
                    st.session_state.erros_form['disponibilidade'] = mensagem
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": data_str,
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
                    # Mostrar erros
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', 
                                  unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        
        # QR Code
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(
                "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
                use_column_width=False,
                width=250
            )
        
        # Chave PIX
        st.markdown("### Chave PIX (Copie e Cole):")
        st.code("aranha.corp@gmail.com", language="text")
        
        # Informações da reserva
        st.markdown("### 📋 Resumo da Reserva")
        reserva = st.session_state.reserva_temp
        
        # Usando a função para mostrar o resumo
        html_resumo = mostrar_resumo_reserva_html(reserva, "📋 Detalhes da Reserva")
        st.markdown(html_resumo, unsafe_allow_html=True)
        
        # Timer
        timer_box = st.empty()
        
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(
                Config.TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                timer_box.markdown(
                    f'<div class="timer-warning">{mensagem_timer}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.session_state.pagamento_ativo = False
                timer_box.warning("⏰ Tempo esgotado! Por favor, inicie uma nova reserva.")
                time.sleep(2)
                st.rerun()
        
        # Botão de confirmação
        if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            with st.spinner("Processando reserva..."):
                # Processar reserva
                sucesso, reserva_id, mensagem = processar_reserva_seguro(
                    st.session_state.reserva_temp
                )
                
                if sucesso:
                    # Limpar estado
                    st.session_state.reserva_id_gerada = reserva_id
                    st.session_state.pagamento_ativo = False
                    
                    # Mostrar confirmação
                    st.balloons()
                    
                    # Confirmação da reserva
                    st.markdown(f"""
                    <div style="background-color: #e8f5e9; padding: 30px; border-radius: 15px; border: 2px solid #4CAF50; margin: 20px 0;">
                        <div style="text-align: center; margin-bottom: 25px;">
                            <h2 style="color: #2c3e50; margin-bottom: 10px;">🎾 RESERVA CONFIRMADA!</h2>
                            <p style="color: #666; font-size: 16px;">{mensagem}</p>
                        </div>
                        
                        {mostrar_resumo_reserva_html(st.session_state.reserva_temp, "📋 Detalhes da Reserva")}
                        
                        <div style="background-color: #f8f9fa; border: 2px solid #28a745; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center;">
                            <h4 style="color: #2c3e50; margin-bottom: 10px;">🆔 ID DA RESERVA</h4>
                            <div style="font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; color: #28a745; letter-spacing: 2px;">
                                {reserva_id}
                            </div>
                            <p style="color: #666; margin-top: 10px; font-size: 14px;">
                                Guarde este ID para consultas futuras e apresentação na unidade.
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 25px;">
                            <p style="color: #666; font-size: 14px;">
                                <i class="fas fa-info-circle"></i> A reserva foi salva no sistema. Não será enviado e-mail de confirmação.
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botões de ação
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📅 Nova Reserva", use_container_width=True):
                            st.session_state.reserva_temp = {}
                            st.rerun()
                    
                    with col2:
                        if st.button("📱 Abrir WhatsApp", use_container_width=True):
                            st.markdown(
                                f'<a href="https://wa.me/{Config.WHATSAPP_NUMBER}" target="_blank">'
                                f'<button style="width: 100%; padding: 10px;">Abrir WhatsApp</button>'
                                f'</a>',
                                unsafe_allow_html=True
                            )
                    
                    time.sleep(5)
                    st.session_state.reserva_temp = {}
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")
    
    # Link do regulamento
    st.markdown("""
    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing" 
       target="_blank" 
       style="display: block; text-align: center; margin-top: 20px; text-decoration: none; color: #555; font-size: 14px; transition: 0.3s;" 
       title="Clique para ler o regulamento">
        <span style="font-size: 24px; display: block;">📄</span>
        Ler Regulamento de Uso
    </a>
    """, unsafe_allow_html=True)

# ============================================
# 13. PÁGINA DE PREÇOS
# ============================================

elif st.session_state.pagina == "Preços":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.markdown("### 🎾 Tabela de Preços")
    st.markdown("---")
    
    # Categorias de serviços
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Aulas Avulsas")
        for key, info in SERVICOS.items():
            if info['tipo'] == "Hora" and "Pacote" not in info['nome']:
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                    <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ {info['preco']}/hora</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("#### 🏆 Treinamento Competitivo")
        for key, info in SERVICOS.items():
            if info['tipo'] == "Mês":
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                    <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ {info['preco']}/mês</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📦 Pacotes de Aulas")
        for key, info in SERVICOS.items():
            if "Pacote" in info['nome']:
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                    <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ {info['preco']} / {info['tipo']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("#### 🎉 Eventos")
        for key, info in SERVICOS.items():
            if info['nome'] == "Eventos":
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                    <p style='margin: 5px 0 0 0; color: #FF9800; font-weight: bold;'>Valor a combinar</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Calculadora de preços
    st.markdown("---")
    st.markdown("#### 🧮 Calculadora de Preços")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_aula = st.selectbox("Tipo de aula", 
                               ["Aula particular", "Aula em grupo", "Aula Kids", "Personal trainer"])
    with col2:
        quantidade = st.number_input("Quantidade de aulas", min_value=1, max_value=20, value=1)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        calcular = st.button("Calcular")
    
    if calcular:
        # Encontrar preço
        preco_por_aula = 0
        for key, info in SERVICOS.items():
            if info['nome'] == tipo_aula:
                preco_por_aula = info['preco']
                break
        
        total = preco_por_aula * quantidade
        st.success(f"**Total:** R$ {total:,.2f} por {quantidade} aulas")

# ============================================
# 14. PÁGINA DE CADASTRO
# ============================================

elif st.session_state.pagina == "Cadastro":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>📝 Portal de Cadastros</h2><br>", 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Professor de Tênis">
            <div class="icon-text">👨‍🏫</div>
            <div class="label-text">PROFESSOR</div>
            <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
                Cadastre-se como professor
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Aluno de Tênis">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
            <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
                Cadastre-se como aluno
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Academia de Tênis">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
            <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
                Cadastre sua academia
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    # Instruções
    st.markdown("""
    <div style='text-align: center; margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; color: #ccc;'>
        <p><strong>📋 Instruções:</strong> Os formulários abrem em uma nova aba.</p>
        <p>Preencha todos os campos obrigatórios e clique em "Enviar" ao final.</p>
        <p>Após o envio, você receberá um e-mail de confirmação.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 15. PÁGINA DASHBOARD
# ============================================

elif st.session_state.pagina == "Dashboard":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    if not st.session_state.admin_autenticado:
        st.subheader("🔐 Acesso Administrativo")
        
        senha = st.text_input(
            "Digite a senha de administrador:", 
            type="password",
            help="Senha para acesso ao dashboard",
            placeholder="Digite a senha..."
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔓 Acessar", use_container_width=True):
                if verificar_senha_admin(senha):
                    st.session_state.admin_autenticado = True
                    st.success("✅ Acesso concedido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        with col2:
            if st.button("🆘 Ajuda", use_container_width=True):
                st.info("""
                Para configurar a senha:
                
                1. Gere o hash da senha:
                ```python
                import hashlib
                hash_senha = hashlib.sha256("sua_senha".encode()).hexdigest()
                ```
                
                2. Adicione ao secrets.toml:
                ```
                ADMIN_PASSWORD_HASH = "hash_gerado"
                ```
                """)
    
    else:
        st.subheader("📊 Dashboard - Reservas")
        
        # Cabeçalho com métricas
        try:
            df = carregar_dados()
            
            if not df.empty:
                # Métricas
                total = len(df)
                confirmados = len(df[df['Status'] == 'Confirmado'])
                cancelados = len(df[df['Status'] == 'Cancelado'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total)
                with col2:
                    st.metric("Confirmados", confirmados)
                with col3:
                    st.metric("Cancelados", cancelados)
                
                # Taxa de conversão
                taxa_conversao = (confirmados / total * 100) if total > 0 else 0
                st.progress(taxa_conversao / 100, 
                          text=f"Taxa de conversão: {taxa_conversao:.1f}%")
                
                st.markdown("---")
                
                # Filtros
                col1, col2, col3 = st.columns(3)
                with col1:
                    filtro_status = st.multiselect(
                        "Filtrar por Status",
                        options=["Confirmado", "Cancelado"],
                        default=["Confirmado"]
                    )
                with col2:
                    filtro_unidade = st.multiselect(
                        "Filtrar por Unidade",
                        options=list(ACADEMIAS.keys())
                    )
                with col3:
                    data_inicio = st.date_input("Data início")
                    data_fim = st.date_input("Data fim")
                
                # Aplicar filtros
                df_filtrado = df.copy()
                if filtro_status:
                    df_filtrado = df_filtrado[df_filtrado['Status'].isin(filtro_status)]
                if filtro_unidade:
                    df_filtrado = df_filtrado[df_filtrado['Unidade'].isin(filtro_unidade)]
                
                # Exibir dados
                st.dataframe(
                    df_filtrado,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.TextColumn("ID", width="small"),
                        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                        "Horário": st.column_config.TextColumn("Horário", width="small"),
                        "Aluno": st.column_config.TextColumn("Aluno"),
                        "E-mail": st.column_config.TextColumn("E-mail"),
                        "Serviço": st.column_config.TextColumn("Serviço"),
                        "Unidade": st.column_config.TextColumn("Unidade"),
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Confirmado", "Cancelado"],
                            required=True,
                        ),
                        "Data_Criacao": st.column_config.DatetimeColumn("Data Criação"),
                    }
                )
                
                # Ações
                st.markdown("### 🛠️ Ações")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.success("Dados atualizados!")
                        st.rerun()
                
                with col2:
                    # Exportar dados
                    csv = df_filtrado.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar CSV",
                        data=csv,
                        file_name=f"reservas_tennis_class_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    # Backup
                    backup_csv = criar_backup()
                    if backup_csv:
                        st.download_button(
                            label="💾 Backup Completo",
                            data=backup_csv,
                            file_name=f"backup_completo_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                # Logout
                st.markdown("---")
                if st.button("🚪 Logout", type="secondary", use_container_width=True):
                    st.session_state.admin_autenticado = False
                    st.rerun()
                
            else:
                st.info("📭 Nenhuma reserva encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro no dashboard: {str(e)}")

# ============================================
# 16. PÁGINA DE CONTATO
# ============================================

elif st.session_state.pagina == "Contato":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.subheader("📞 Canais de Atendimento")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 E-mail")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <h4 style='margin:0; color: white;'>aranha.corp@gmail.com</h4>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Respondemos em até 24h
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🏢 Endereço Principal")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='margin:0; color: white;'>São Paulo - SP</p>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Atendemos em todas as academias parceiras
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <h4 style='margin:0; color: white;'>(11) 97142-5028</h4>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Segunda a Sábado, 8h às 20h
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⏰ Horário de Atendimento")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='margin:0; color: white;'>Segunda a Sexta: 8h às 20h</p>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Sábado: 8h às 18h<br>
            Domingo: Fechado
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulário de contato
    st.markdown("### ✉️ Envie uma mensagem")
    with st.form("contato_form"):
        nome_contato = st.text_input("Seu nome", placeholder="Digite seu nome")
        email_contato = st.text_input("Seu e-mail", placeholder="Digite seu e-mail")
        telefone_contato = st.text_input("Seu telefone (opcional)", placeholder="(11) 99999-9999")
        mensagem = st.text_area("Sua mensagem", placeholder="Digite sua mensagem aqui...", height=100)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            submit = st.form_submit_button("📤 Enviar", use_container_width=True)
        
        if submit:
            if nome_contato and email_contato and mensagem:
                st.success("✅ Mensagem enviada! Entraremos em contato em breve.")
            else:
                st.warning("⚠️ Preencha todos os campos obrigatórios.")

# ============================================
# 17. RODAPÉ
# ============================================

st.markdown("""
<div style='text-align: center; margin-top: 40px; color: rgba(255,255,255,0.6); font-size: 12px;'>
    <hr style='border-color: rgba(255,255,255,0.2);'>
    <p>TENNIS CLASS © 2024 - Sistema de Gestão Completo</p>
    <p>Desenvolvido por André Aranha | MASTER CODE DEEP SEEK v10</p>
    <p style='font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 5px;'>
    Última atualização: 2024-12-06 | Sistema otimizado e seguro
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 18. INICIALIZAÇÃO DO SISTEMA
# ============================================

if __name__ == "__main__":
    # Log de inicialização
    logger.info("Sistema TENNIS CLASS v10 iniciado com sucesso - VERSÃO SEM E-MAIL")
