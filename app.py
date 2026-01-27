import streamlit as st
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (Usando seus Secrets configurados)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro na conexão com a planilha. Verifique os Secrets.")

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_confirmacao(dados):
    try:
        remetente = "aranha.corp@gmail.com.br"
        senha = st.secrets["EMAIL_PASSWORD"] 
        
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class"
        
        corpo = f"""
        Olá {dados['Aluno']}, sua reserva foi confirmada!
        
        DETALHES DA AULA:
        📅 Data: {dados['Data']}
        ⏰ Horário: {dados['Hora']}
        📍 Local: {dados['Local']}
        🎾 Serviço: {dados['Servico']}
        
        Prepare sua raquete!
        Equipe Tennis Class
        """
        msg.attach(MIMEText(corpo, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, [dados['Email'], remetente], msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento' not in st.session_state: st.session_state.pagamento = False

# 4. ESTILIZAÇÃO CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-attachment: fixed;
    }
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px; border-radius: 20px; color: black;
    }
    .sidebar-title { color: white; font-weight: bold; font-size: 18px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# 5. MENU LATERAL (SIDEBAR RESTAURADA)
with st.sidebar:
    st.image("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png", width=150)
    st.markdown("### 🎾 NAVEGAÇÃO")
    if st.button("Página Inicial (Reservas)", use_container_width=True): 
        st.session_state.pagina = "Home"
        st.session_state.pagamento = False
    if st.button("Nossos Serviços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Loja de Produtos", use_container_width=True): st.session_state.pagina = "Produtos"
    if st.button("Área de Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Fale Conosco", use_container_width=True): st.session_state.pagina = "Contato"
    
    st.markdown("---")
    st.markdown('<p class="sidebar-title">🏢 Academias Recomendadas</p>', unsafe_allow_html=True)
    st.info("📍 Play Tennis Ibirapuera\n\n📍 Top One Tennis\n\n📍 Fontes & Barbeta\n\n📍 Arena BTG")

# 6. LÓGICA DAS PÁGINAS

# PÁGINA HOME
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align:center; color:white;'>TENNIS CLASS</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if not st.session_state.pagamento:
