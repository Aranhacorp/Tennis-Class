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

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}

# 4. FUNÇÃO DE ENVIO DE E-MAIL (Senha: image_31667b)
def enviar_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" # Senha de app verificada
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = remetente, dados['Email_Aluno']
        msg['Subject'] = "Reserva Confirmada - TENNIS CLASS"
        corpo = f"Olá {dados['Aluno']},\n\nSua aula está agendada!\nLocal: {dados['Academia']}\nData/Hora: {dados['Data']} às {dados['Horario']}\nServiço: {dados['Servico']}"
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# 5. DESIGN E ESTILO (CSS)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-attachment: fixed;
    }
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .custom-card { background-color: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 20px; color: #333; }
    .translucent-balloon { background-color: rgba(60, 60, 60, 0.8); padding: 25px; border-radius: 15px; color: white; backdrop-filter: blur(10px); }
    .btn-cadastro { display: block; width: 100%; background-color: #1e5e20; color: white !important; padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; }
    .assinatura-aranha { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
""", unsafe_allow_html=True)

# 6. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    opcoes = ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]
    for opcao in opcoes:
        if st.button(opcao, use_container_width=True):
            st.session_state.pagina = opcao
            st.session_state.pagamento_ativo = False
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 7. LÓGICA DE NAVEGAÇÃO
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendamento")
            col1, col2 = st.columns(2)
            aluno = col1.text_input("Nome do Aluno")
            email = col2.text_input("E-mail")
            servico = st.selectbox("Escolha o Serviço", [
                "Aula Individual R$ 250/hora", "Aula em Grupo R$ 200/hora", 
                "Aula Kids R$ 200/hora", "Treinamento Competitivo R$ 1.200/mês", 
                "Eventos valor a combinar"
            ])
            local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Fontes & Barbeta", "Arena BTG"])
            data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("RESERVAR E IR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%Y-%m-%d"), "Horario": hora_aula,
                        "Aluno": aluno, "Servico": servico, "Status": "Pendente",
                        "Academia": local, "Email_Aluno": email
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
    else:
        st.subheader("💳 Pagamento PIX")
        st.write(f"**Aluno:** {st.session_state.reserva_temp['Aluno']}")
        st.markdown("**Chave PIX:** aranha.corp@gmail.com") # Chave antes do e-mail
        if st.button("CONFIRMAR AGENDAMENTO"):
            try:
                # Gravação robusta
                df_existente = conn.read(worksheet="Página1")
                df_novo = pd.concat([df_existente, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
