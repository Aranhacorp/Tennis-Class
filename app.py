import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro na conexão com a planilha. Verifique o Secrets.")

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_confirmacao(dados):
    try:
        remetente = "aranha.corp@gmail.com.br"
        # Utiliza a senha de app 'xmtw pnyq wsav iock' configurada no seu Secrets
        senha = st.secrets["EMAIL_PASSWORD"] 
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class"
        corpo = f"Olá {dados['Aluno']},\n\nSua reserva foi confirmada!\n\n📅 Data: {dados['Data']}\n⏰ Hora: {dados['Hora']}\n📍 Local: {dados['Local']}\n🎾 Serviço: {dados['Servico']}\n\nAté logo!\nBy Andre Aranha"
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, [dados['Email'], remetente], msg.as_string())
        server.quit()
        return True
    except Exception: return False

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento' not in st.session_state: st.session_state.pagamento = False

# 4. ESTILIZAÇÃO CSS (Balões cinzas, Assinatura e WhatsApp)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-attachment: fixed;
    }
    /* Balão Cinza Translúcido solicitado */
    .translucent-balloon {
        background-color: rgba(60, 60, 60, 0.65);
        padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);
        color: white; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .main-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: black; }
    
    /* Assinatura no rodapé */
    .footer-signature {
        position: fixed; left: 10px; bottom: 10px; color: rgba(255,255,255,0.5); font-size: 12px; z-index: 100;
    }
    
    /* Ícone Flutuante WhatsApp */
    .whatsapp-button {
        position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px;
        background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center;
        font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 100;
    }
</style>

<div class="footer-signature">by Andre Aranha</div>
<a href="https://wa.me/5511971425028" class="whatsapp-button" target="_blank">
    <i style="margin-top:16px" class="fa fa-whatsapp"></i>
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" style="width:100%; padding:10px;">
</a>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
""", unsafe_allow_html=True)

#
