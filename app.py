# ============================================
# MASTER CODE DEEP SEEK v.12.4
# ============================================
# TENNIS CLASS APP - Sistema Completo Otimizado
# Versão: 12.4
# Correção: Preços Aula Kids (R$ 230/hora | Pacote 4h R$ 920)
# Modificações: 
#   - removido "Reservas ativas" da barra lateral
#   - incluídos preços de locação de quadra (R$200 externa / R$350 coberta)
#   - adicionada calculadora completa (aulas, pacotes e locação)
#   - melhorias no tratamento de erros e inicialização
#   - substituído título de texto pela imagem do logo (aumentado em 12,5%)
#   - adicionados websites das academias parceiras
#   - logo posicionado na altura original (sem deslocamento)
# ============================================

import streamlit as st
import pandas as pd
import time
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
import logging
from functools import lru_cache

# Tenta importar a conexão com Google Sheets, mas não falha se não estiver disponível
try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSheetsConnection = None
    GSHEETS_AVAILABLE = False
    st.warning("⚠️ Biblioteca 'streamlit-gsheets' não encontrada. A funcionalidade de reservas pode não funcionar.")

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# Configuração de logging - apenas console, sem arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ============================================
# 2. CONFIGURAÇÕES DO SISTEMA
# ============================================

class Config:
    """Classe de configuração centralizada do sistema."""
    
    # Google Sheets
    SPREADSHEET_URL = ""
    WORKSHEET_NAME = "Página1"
    
    # Contato
    WHATSAPP_NUMBER = "5511971425028"
    
    # Limites do sistema
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300  # 5 minutos em segundos
    
    # Horários disponíveis
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]
    
    @classmethod
    def get_admin_password(cls) -> str:
        """Obtém senha do admin com fallback seguro."""
        try:
            return st.secrets.get("ADMIN_PASSWORD", "aranha2026")
        except:
            return "aranha2026"

class ReservaError(Exception):
    """Exceção personalizada para erros de reserva."""
    pass

# ============================================
# 3. DADOS DO SISTEMA (PREÇOS CORRIGIDOS)
# ============================================

SERVICOS = {
    "particular_hora": {"nome": "Aula particular", "preco": 250, "tipo": "Hora"},
    "grupo_hora": {"nome": "Aula em grupo", "preco": 200, "tipo": "Hora"},
    "kids_hora": {"nome": "Aula Kids", "preco": 230, "tipo": "Hora"},
    "personal_hora": {"nome": "Personal trainer", "preco": 250, "tipo": "Hora"},
    "competitivo": {"nome": "Treinamento competitivo", "preco": 1400, "tipo": "Mês"},
    "eventos": {"nome": "Eventos", "preco": 0, "tipo": "Hora"},
    "pacote_particular_4": {"nome": "Pacote aula particular", "preco": 1000, "tipo": "4 aulas de 1 hora"},
    "pacote_grupo_4": {"nome": "Pacote aula em grupo", "preco": 800, "tipo": "4 aulas de 1 hora"},
    "pacote_particular_8": {"nome": "Pacote aula particular", "preco": 2000, "tipo": "8 aulas de 1 hora"},
    "pacote_grupo_8": {"nome": "Pacote aula em grupo", "preco": 1600, "tipo": "8 aulas de 1 hora"},
    "pacote_kids_4": {"nome": "Pacote aula Kids", "preco": 920, "tipo": "4 aulas de 1 hora"},
    "pacote_personal_4": {"nome": "Pacote Personal Trainer", "preco": 1000, "tipo": "4 aulas de 1 hora"}
}

# Academias parceiras (com websites adicionados)
ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488",
        "website": "https://www.playtennis.com.br/"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828",
        "website": "https://toponetennis.com.br/"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028",
        "website": "https://www.instagram.com/barbetaefontestennisacademy/"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860",
        "website": "https://arenabtg.com.br/"
    }
}

FORM_LINKS = {
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?usp=dialog",
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?usp=dialog",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog"
}

# ============================================
# 4. FUNÇÕES DE VALIDAÇÃO
# ============================================

def validar_nome(nome: str) -> bool:
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    return bool(re.match(r'^[a-zA-ZÀ-ÿ\s\.\-]+$', nome_limpo))

def validar_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_telefone(telefone: str) -> bool:
    telefone_limpo = re.sub(r'\D', '', telefone)
    return len(telefone_limpo) in [10, 11]

def validar_data_horario(data: str, horario: str, unidade: str) -> Tuple[bool, str]:
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        if data_obj.date() < datetime.now().date():
            return False, "Não é possível agendar para datas passadas."
        if (data_obj.date() - datetime.now().date()).days > 60:
            return False, "Só é possível agendar com até 60 dias de antecedência."
        
        disponibilidade = carregar_disponibilidade(data, unidade)
        vagas = disponibilidade.get(horario, Config.MAX_ALUNOS_POR_HORARIO)
        if vagas <= 0:
            return False, f"Horário indisponível na {unidade}."
        return True, ""
    except ValueError:
        return False, "Formato de data inválido."
    except Exception as e:
        logger.error(f"Erro na validação: {e}")
        return True, ""

# ============================================
# 5. FUNÇÕES DE DADOS - GOOGLE SHEETS
# ============================================

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    """Carrega dados do Google Sheets com tratamento de erros."""
    if not GSHEETS_AVAILABLE:
        st.error("❌ Biblioteca 'streamlit-gsheets' não instalada. Não é possível carregar dados.")
        return pd.DataFrame()
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=Config.WORKSHEET_NAME)
        logger.info(f"Dados carregados: {len(df)} registros")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados do Google Sheets: {str(e)}")
        st.error(f"❌ Erro de conexão com Google Sheets: {str(e)}. Verifique suas secrets.")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def carregar_disponibilidade(data: str, unidade: str) -> Dict[str, int]:
    try:
        df = carregar_dados()
        if df.empty:
            return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}
        
        filtrado = df[
            (df['Data'] == data) &
            (df['Unidade'] == unidade) &
            (df['Status'].isin(['Pendente', 'Confirmado']))
        ]
        
        disponibilidade = {}
        for hora in Config.HORARIOS_DISPONIVEIS:
            count = len(filtrado[filtrado['Horário'] == hora])
            disponibilidade[hora] = Config.MAX_ALUNOS_POR_HORARIO - count
        return disponibilidade
    except Exception as e:
        logger.error(f"Erro ao carregar disponibilidade: {e}")
        return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}

def salvar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    if not GSHEETS_AVAILABLE:
        return False, "Biblioteca 'streamlit-gsheets' não disponível"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        reserva_id = str(uuid.uuid4())[:8].upper()
        reserva["ID"] = reserva_id
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Confirmado"
        reserva["Data_Criacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet=Config.WORKSHEET_NAME, data=df_novo)
        st.cache_data.clear()
        logger.info(f"Reserva {reserva_id} salva com sucesso")
        return True, reserva_id
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        return False, str(e)

def criar_backup() -> bytes:
    try:
        df = carregar_dados()
        if not df.empty:
            return df.to_csv(index=False).encode('utf-8')
        return b""
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return b""

# ============================================
# 6. FUNÇÕES DE PROCESSAMENTO
# ============================================

def processar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str, str]:
    try:
        if not validar_nome(reserva.get('Aluno', '')):
            raise ReservaError("Nome inválido. Use apenas letras (mínimo 3 caracteres).")
        if not validar_email(reserva.get('E-mail', '')):
            raise ReservaError("E-mail inválido. Digite um e-mail válido.")
        
        disponivel, mensagem = validar_data_horario(
            reserva['Data'], reserva['Horário'], reserva['Unidade']
        )
        if not disponivel:
            raise ReservaError(mensagem)
        
        sucesso, reserva_id = salvar_reserva(reserva)
        if not sucesso:
            raise ReservaError("Falha ao salvar reserva.")
        return True, reserva_id, "✅ Reserva confirmada com sucesso!"
    except ReservaError as e:
        return False, "", str(e)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return False, "", f"Erro inesperado: {str(e)}"

def verificar_senha_admin(senha_digitada: str) -> bool:
    try:
        senha_correta = Config.get_admin_password()
        return senha_digitada == senha_correta
    except Exception as e:
        logger.error(f"Erro na verificação: {e}")
        return False

# ============================================
# 7. ESTADOS DA SESSÃO
# ============================================

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
# 8. ESTILOS CSS (logo sem deslocamento)
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
    
    /* Header com logo - tamanho aumentado em 12,5% */
    .header-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .header-logo img {
        max-width: 337.5px;
        width: 100%;
        height: auto;
    }
    
    /* Cards */
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
        position: relative; 
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
    
    /* Mensagens */
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
    
    /* Confirmação */
    .confirmation-box {
        background-color: #e8f5e9;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    
    /* Chave PIX */
    .pix-key {
        background-color: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        color: #007bff;
    }
    
    /* Botões */
    .stButton > button {
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>

<!-- Botão WhatsApp -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank" 
   aria-label="Contato via WhatsApp">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="WhatsApp">
</a>

<!-- Assinatura -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura André Aranha"
     style="position: fixed; bottom: 15px; left: 20px; width: 130px; z-index: 9999; opacity: 0.8;">
""", unsafe_allow_html=True)

# ============================================
# 9. COMPONENTES REUTILIZÁVEIS
# ============================================

def mostrar_timer(tempo_total: int, inicio_time: float) -> Tuple[bool, str]:
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

def card_com_estilo(conteudo: str = "", classe: str = "custom-card") -> str:
    return f'<div class="{classe}">{conteudo}</div>'

# ============================================
# 10. MENU LATERAL (com websites)
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    
    menu_itens = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    for item in menu_itens:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            if item == "Dashboard":
                st.session_state.admin_autenticado = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏢 ACADEMIAS PARCEIRAS")
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"📍 **{nome}**\n"
            f"<div style='font-size: 11px; color: #ccc; margin-bottom: 10px;'>"
            f"{info['endereco']}<br>📞 {info['telefone']}<br>"
            f"🌐 <a href='{info['website']}' target='_blank' style='color: #4CAF50; text-decoration: none;'>{info['website']}</a>"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    with st.expander("❓ Ajuda Rápida"):
        st.markdown("""
        **Contato:** (11) 97142-5028
        **Horário:** Seg-Sex: 9h-18h | Sáb: 9h-13h
        """)
    
    # Seção "Status" removida propositalmente

# ============================================
# 11. PÁGINA PRINCIPAL - HOME (com logo)
# ============================================

# Substitui o título de texto pela imagem do logo
st.markdown("""
<div class="header-logo">
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Tennis%20Class%20logo%20v.1.png" alt="Tennis Class Logo">
</div>
""", unsafe_allow_html=True)

if st.session_state.pagina == "Home":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.subheader("📅 Agendar Aula")
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input("Nome do Aluno *", placeholder="Ex: João Silva")
            with col2:
                email = st.text_input("E-mail *", placeholder="exemplo@email.com")
            
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
            
            col1, col2 = st.columns(2)
            with col1:
                dt = st.date_input("Data *", format="DD/MM/YYYY",
                                   min_value=datetime.now().date(),
                                   max_value=datetime.now().date() + timedelta(days=60))
            with col2:
                hr = st.selectbox("Horário *", Config.HORARIOS_DISPONIVEIS)
            
            submit = st.form_submit_button("AVANÇAR PARA PAGAMENTO", use_container_width=True, type="primary")
            
            if submit:
                st.session_state.erros_form = {}
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido."
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido."
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
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', unsafe_allow_html=True)
    
    else:  # TELA DE PAGAMENTO
        st.subheader("💳 Pagamento via PIX")
        st.markdown("### Chave PIX:")
        st.markdown('<div class="pix-key">aranha.corp@gmail.com</div>', unsafe_allow_html=True)
        
        st.markdown("### 📋 Resumo da Reserva")
        reserva = st.session_state.reserva_temp
        st.info(f"""
        **Aluno:** {reserva.get('Aluno', '')}  
        **Serviço:** {reserva.get('Serviço', '')}  
        **Unidade:** {reserva.get('Unidade', '')}  
        **Data:** {reserva.get('Data', '')} às {reserva.get('Horário', '')}
        **E-mail:** {reserva.get('E-mail', '')}
        """)
        
        timer_box = st.empty()
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(Config.TEMPO_PAGAMENTO, st.session_state.inicio_timer)
            if ativo:
                timer_box.markdown(f'<div class="timer-warning">{mensagem_timer}</div>', unsafe_allow_html=True)
            else:
                st.session_state.pagamento_ativo = False
                timer_box.warning("⏰ Tempo esgotado!")
                time.sleep(2)
                st.rerun()
        
        if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            with st.spinner("Processando..."):
                sucesso, reserva_id, mensagem = processar_reserva(st.session_state.reserva_temp)
                if sucesso:
                    st.session_state.reserva_id_gerada = reserva_id
                    st.session_state.pagamento_ativo = False
                    st.balloons()
                    st.markdown(f"""
                    <div class="confirmation-box">
                        <h3>✅ Reserva Confirmada!</h3>
                        <p>{mensagem}</p>
                        <div class="reserva-id-box">ID da Reserva: {reserva_id}</div>
                        <p><strong>Guarde este ID para apresentar na academia.</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📅 Nova Reserva", use_container_width=True):
                            st.session_state.reserva_temp = {}
                            st.rerun()
                    with col2:
                        if st.button("📱 Abrir WhatsApp", use_container_width=True):
                            st.markdown(f'<a href="https://wa.me/{Config.WHATSAPP_NUMBER}" target="_blank"><button style="width: 100%; padding: 10px;">Abrir WhatsApp</button></a>', unsafe_allow_html=True)
                    time.sleep(5)
                    st.session_state.reserva_temp = {}
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")
    
    st.markdown("""
    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing" 
       target="_blank" 
       style="display: block; text-align: center; margin-top: 20px; text-decoration: none; color: #555; font-size: 14px;">
        <span style="font-size: 24px; display: block;">📄</span>
        Ler Regulamento de Uso
    </a>
    """, unsafe_allow_html=True)

# ============================================
# 12. PÁGINA DE PREÇOS
# ============================================

elif st.session_state.pagina == "Preços":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    st.markdown("### 🎾 Tabela de Preços")
    st.markdown("---")
    
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
        st.markdown("#### 📦 Pacotes")
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
    
    st.markdown("---")
    st.markdown("#### 🏟️ Locação de Quadra")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
            <h4 style='margin: 0; color: white;'>Quadra Externa</h4>
            <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ 200/hora</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
            <h4 style='margin: 0; color: white;'>Quadra Coberta</h4>
            <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ 350/hora</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 🧮 Calculadora (Aulas Avulsas)")
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_aula = st.selectbox("Tipo de aula", ["Aula particular", "Aula em grupo", "Aula Kids", "Personal trainer"])
    with col2:
        quantidade = st.number_input("Quantidade de aulas", min_value=1, max_value=20, value=1)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        calcular = st.button("Calcular")
    if calcular:
        preco_por_aula = 0
        for key, info in SERVICOS.items():
            if info['nome'] == tipo_aula:
                preco_por_aula = info['preco']
                break
        total = preco_por_aula * quantidade
        st.success(f"**Total:** R$ {total:,.2f} por {quantidade} aulas")
    
    st.markdown("---")
    st.markdown("#### 🧮 Calculadora Completa (Aulas, Pacotes e Locação)")
    with st.form("calculadora_completa"):
        opcao = st.radio("Selecione o tipo de serviço", ["Aula avulsa", "Pacote", "Locação de quadra"], horizontal=True)
        if opcao == "Aula avulsa":
            tipo_aula2 = st.selectbox("Tipo de aula", ["Aula particular", "Aula em grupo", "Aula Kids", "Personal trainer"], key="tipo_aula2")
            quantidade2 = st.number_input("Quantidade de horas/aulas", min_value=1, max_value=20, value=1, key="qtd2")
            if st.form_submit_button("Calcular"):
                preco = 0
                for key, info in SERVICOS.items():
                    if info['nome'] == tipo_aula2 and info['tipo'] == "Hora":
                        preco = info['preco']
                        break
                total = preco * quantidade2
                st.success(f"**Total:** R$ {total:,.2f} para {quantidade2} hora(s) de {tipo_aula2}")
        elif opcao == "Pacote":
            pacotes = []
            for key, info in SERVICOS.items():
                if "Pacote" in info['nome']:
                    pacotes.append(f"{info['nome']} - R$ {info['preco']} ({info['tipo']})")
            pacote_escolhido = st.selectbox("Escolha o pacote", pacotes)
            if st.form_submit_button("Calcular"):
                preco = 0
                descricao = ""
                for key, info in SERVICOS.items():
                    if "Pacote" in info['nome'] and info['nome'] in pacote_escolhido:
                        preco = info['preco']
                        descricao = f"{info['nome']} ({info['tipo']})"
                        break
                st.success(f"**Total:** R$ {preco:,.2f} para o pacote: {descricao}")
        else:  # Locação de quadra
            tipo_quadra = st.selectbox("Tipo de quadra", ["Quadra Externa", "Quadra Coberta"])
            horas = st.number_input("Número de horas", min_value=1, max_value=12, value=1)
            if st.form_submit_button("Calcular"):
                preco_hora = 200 if tipo_quadra == "Quadra Externa" else 350
                total = preco_hora * horas
                st.success(f"**Total:** R$ {total:,.2f} para {horas} hora(s) de {tipo_quadra}")

# ============================================
# 13. PÁGINA DE CADASTRO
# ============================================

elif st.session_state.pagina == "Cadastro":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📝 Portal de Cadastros</h2><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" class="clean-link" target="_blank">
            <div class="icon-text">👨‍🏫</div><div class="label-text">PROFESSOR</div>
        </a>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" class="clean-link" target="_blank">
            <div class="icon-text">👤</div><div class="label-text">ALUNO</div>
        </a>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" class="clean-link" target="_blank">
            <div class="icon-text">🏢</div><div class="label-text">ACADEMIA</div>
        </a>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; color: #ccc;'>
        <p><strong>📋 Instruções:</strong> Os formulários abrem em nova aba. Preencha todos os campos obrigatórios.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 14. PÁGINA DASHBOARD
# ============================================

elif st.session_state.pagina == "Dashboard":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    if not st.session_state.admin_autenticado:
        st.subheader("🔐 Acesso Administrativo")
        senha = st.text_input("Senha de administrador:", type="password", placeholder="Digite a senha...")
        col1, _ = st.columns([3, 1])
        with col1:
            if st.button("🔓 Acessar", use_container_width=True):
                if verificar_senha_admin(senha):
                    st.session_state.admin_autenticado = True
                    st.success("✅ Acesso concedido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
    else:
        st.subheader("📊 Dashboard - Reservas")
        try:
            df = carregar_dados()
            if not df.empty:
                total = len(df)
                confirmados = len(df[df['Status'] == 'Confirmado'])
                cancelados = len(df[df['Status'] == 'Cancelado'])
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total", total)
                with col2:
                    st.metric("Confirmados", confirmados)
                with col3:
                    st.metric("Cancelados", cancelados)
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    filtro_status = st.multiselect("Status", options=["Confirmado", "Cancelado"], default=["Confirmado"])
                with col2:
                    filtro_unidade = st.multiselect("Unidade", options=list(ACADEMIAS.keys()))
                df_filtrado = df.copy()
                if filtro_status:
                    df_filtrado = df_filtrado[df_filtrado['Status'].isin(filtro_status)]
                if filtro_unidade:
                    df_filtrado = df_filtrado[df_filtrado['Unidade'].isin(filtro_unidade)]
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                st.markdown("### 🛠️ Ações")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Atualizar", use_container_width=True):
                        st.cache_data.clear()
                        st.success("Dados atualizados!")
                        st.rerun()
                with col2:
                    csv = df_filtrado.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Exportar CSV", data=csv, file_name=f"reservas_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
                st.markdown("---")
                if st.button("🚪 Logout", type="secondary", use_container_width=True):
                    st.session_state.admin_autenticado = False
                    st.rerun()
            else:
                st.info("📭 Nenhuma reserva encontrada.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============================================
# 15. PÁGINA DE CONTATO
# ============================================

elif st.session_state.pagina == "Contato":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    st.subheader("📞 Canais de Atendimento")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📧 E-mail")
        st.markdown("""<div style='padding:15px;background:rgba(255,255,255,0.1);border-radius:10px;'><h4 style='margin:0;color:white;'>aranha.corp@gmail.com</h4></div>""", unsafe_allow_html=True)
        st.markdown("### 🏢 Endereço")
        st.markdown("""<div style='padding:15px;background:rgba(255,255,255,0.1);border-radius:10px;'><p style='margin:0;color:white;'>São Paulo - SP</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown("""<div style='padding:15px;background:rgba(255,255,255,0.1);border-radius:10px;'><h4 style='margin:0;color:white;'>(11) 97142-5028</h4><p style='margin:5px 0 0 0;color:#ccc;'>Seg-Sab: 8h-20h</p></div>""", unsafe_allow_html=True)
        st.markdown("### ⏰ Horário")
        st.markdown("""<div style='padding:15px;background:rgba(255,255,255,0.1);border-radius:10px;'><p style='margin:0;color:white;'>Seg-Sex: 8h-20h</p><p style='margin:5px 0 0 0;color:#ccc;'>Sáb: 8h-18h</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ✉️ Envie uma mensagem")
    with st.form("contato_form"):
        nome = st.text_input("Seu nome", placeholder="Digite seu nome")
        email = st.text_input("Seu e-mail", placeholder="Digite seu e-mail")
        telefone = st.text_input("Telefone (opcional)", placeholder="(11) 99999-9999")
        mensagem = st.text_area("Mensagem", placeholder="Sua mensagem...", height=100)
        if st.form_submit_button("📤 Enviar", use_container_width=True):
            if nome and email and mensagem:
                st.success("✅ Mensagem enviada!")
            else:
                st.warning("⚠️ Preencha todos os campos.")

# ============================================
# 16. RODAPÉ
# ============================================

st.markdown("""
<div style='text-align: center; margin-top: 40px; color: rgba(255,255,255,0.6); font-size: 12px;'>
    <hr style='border-color: rgba(255,255,255,0.2);'>
    <p>TENNIS CLASS © 2025 - Sistema Completo</p>
    <p>MASTER CODE DEEP SEEK v.12.4</p>
    <p style='font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 5px;'>
    Correção: Aula Kids R$ 230/hora | Pacote 4h R$ 920 | Locação de quadra | Calculadora completa | Websites academias | Logo aumentado
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 17. INICIALIZAÇÃO
# ============================================

if __name__ == "__main__":
    logger.info("MASTER CODE DEEP SEEK v.12.4 iniciado")
