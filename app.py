import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide", page_icon="🎾")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'academia_foco' not in st.session_state: st.session_state.academia_foco = None

# 4. FUNÇÃO DE ENVIO DE E-MAIL (SMTP GMAIL)
def enviar_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" # Senha de App Gerada
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = remetente, dados['Email_Aluno']
        msg['Subject'] = "Reserva Confirmada - TENNIS CLASS"
        corpo = f"Olá {dados['Aluno']},\n\nSua reserva foi confirmada!\nLocal: {dados['Academia']}\nData: {dados['Data']} às {dados['Horario']}\nServiço: {dados['Servico']}"
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# 5. DESIGN, ASSINATURA E WHATSAPP FLUTUANTE
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }
    .custom-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: #333; }
    .translucent-balloon { background-color: rgba(50, 50, 50, 0.85); padding: 25px; border-radius: 15px; color: white; backdrop-filter: blur(10px); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
    .btn-cadastro { display: block; width: 100%; background-color: #1e5e20; color: white !important; padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; }
    .sidebar-detalhe { color: #f0f0f0; font-size: 13px; margin: -10px 0 15px 35px; border-left: 2px solid #ff4b4b; padding-left: 10px; }
    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-footer { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; transition: 0.3s; }
    .whatsapp-footer:hover { transform: scale(1.1); }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-footer">
</a>
""", unsafe_allow_html=True)

# 6. MENU LATERAL E ACADEMIAS RECOMENDADAS
info_academias = {
    "PLAY TENNIS Ibirapuera": "R. Estado de Israel, 860 - Vila Clementino, SP<br>📞 (11) 97752-0488",
    "TOP One Tennis": "Av. Indianópolis, 647 - Indianópolis, SP<br>📞 (11) 93236-3828",
    "MELL Tennis": "Rua Oscar Gomes Cardim, 535 - Vila Cordeiro, SP<br>📞 (11) 97142-5028",
    "ARENA BTG Morumbi": "Av. Major Sylvio de Magalhães Padilha, 16741<br>📞 (11) 98854-3860"
}

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
    for nome in info_academias.keys():
        if st.button(f"📍 {nome}", key=f"side_{nome}", use_container_width=True):
            st.session_state.academia_foco = nome if st.session_state.academia_foco != nome else None
        if st.session_state.academia_foco == nome:
            st.markdown(f'<div class="sidebar-detalhe">{info_academias[nome]}</div>
