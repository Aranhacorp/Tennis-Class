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
def enviar_confirmacao_email(dados):
    try:
        remetente = "aranha.corp@gmail.com.br"
        # Importante: Use 'Senha de App' do Google nas configurações da conta
        senha = st.secrets.get("EMAIL_PASSWORD", "sua_senha_de_app_aqui") 
        
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class - {dados['Aluno']}"
        
        corpo = f"""
        Olá {dados['Aluno']},
        
        Sua reserva de aula foi confirmada com sucesso!
        
        DETALHES DA AULA:
        📅 Data: {dados['Data']}
        ⏰ Horário: {dados['Hora']}
        🎾 Serviço: {dados['Servico']}
        📍 Local: {dados['Local']}
        
        Prepare sua raquete, nos vemos na quadra!
        Equipe Tennis Class
        """
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
    
    st.markdown("---")
    info_academias = {
        "Play Tennis Ibirapuera": "R. Joinville, 401 - Vila Mariana<br>📞 (11) 5081-3000",
        "Top One Tennis": "R. João Lourenço, 629 - Vila Nova Conceição<br>📞 (11) 3845-6688",
        "Fontes & Barbeta Tennis": "Av. Prof. Ascendino Reis, 724<br>📞 (11) 99911-3000",
        "Arena BTG": "Av. das Nações Unidas, 13797<br>📞 (11) 94555-2200"
    }
    for nome in info_academias.keys():
        if st.button(f"📍 {nome}", key=f"nav_{nome}", use_container_width=True):
            st.session_state.academia_foco = nome if st.session_state.academia_foco != nome else None
        if st.session_state.academia_foco == nome:
            st.markdown(f'<div class="sidebar-detalhe">{info_academias[nome]}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. PÁGINA HOME: RESERVA
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail do Aluno") # E-mail abaixo do nome
            servico = st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Aulas em Grupo", "Aulas Kids", "Treinamento competitivo", "Clinicas", "Treinamento esportivo", "Eventos"])
            local = st.selectbox("Local", list(info_academias.keys()))
            data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY") # Padrão BR
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%d/%m/%Y"), 
                        "Hora": hora_aula, 
                        "Aluno": aluno, 
                        "Email": email, 
                        "Servico": servico, 
                        "Local": local
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else: st.warning("Por favor, preencha o Nome e o E-mail.")
    else:
        st.markdown("### 💳 Pagamento via PIX")
        st.write("Chave: **aranha.corp@gmail.com.br**")
        if st.button("CONFIRMAR AGENDAMENTO E ENVIAR E-MAIL"):
            st.balloons()
            enviado = enviar_confirmacao_email(st.session_state.reserva_temp)
            if enviado:
                st.success(f"Reserva confirmada! Um e-mail foi enviado para {st.session_state.reserva_temp['Email']}.")
            else:
                st.info("Reserva salva! (Configure a EMAIL_PASSWORD nos Secrets para ativar o envio automático)")
            st.session_state.pagamento_ativo = False
    st.markdown('</div>', unsafe_allow_html=True)

# 7. SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## 🎾 Nossos Serviços")
    for s in ["Aulas Individuais",
