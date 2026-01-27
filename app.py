import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_confirmacao(email_destino, nome_aluno, servico, data, hora, local):
    try:
        # Credenciais da Tennis Class
        remetente = "aranha.corp@gmail.com.br"
        # Importante: Para o Gmail, use uma "Senha de App" gerada na sua conta Google
        senha = st.secrets.get("EMAIL_PASSWORD", "sua_senha_de_app") 
        
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = email_destino
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class - {nome_aluno}"
        
        corpo = f"Olá {nome_aluno},\n\nSua aula de tênis foi agendada com sucesso!\n\nDETALHES:\n📅 Data: {data}\n⏰ Horário: {hora}\n🎾 Serviço: {servico}\n📍 Local: {local}\n\nNos vemos na quadra!\nEquipe Tennis Class"
        msg.attach(MIMEText(corpo, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'academia_foco' not in st.session_state: st.session_state.academia_foco = None

# 4. DESIGN E ESTILO
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    .custom-card {
        background-color: rgba(255, 255, 255, 0.9) !important; 
        padding: 30px; border-radius: 20px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: #333 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .btn-cadastro {
        display: block; width: 100%; background-color: #1e5e20; color: white !important;
        padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold;
    }
    .sidebar-detalhe {
        text-align: left !important; color: #f0f0f0; font-size: 13px; 
        margin: -10px 0 15px 35px; border-left: 2px solid #ff4b4b; padding-left: 10px;
    }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" style="position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000;">
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.session_state.academia_foco = None
            st.rerun()
    
    st.markdown("---
