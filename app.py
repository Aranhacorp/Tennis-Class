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

# 3. ESTADOS DA SESSÃO (Essencial para evitar erros de navegação)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 4. FUNÇÃO DE ENVIO DE E-MAIL (Senha: xmtw pnyq wsav iock)
def enviar_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" 
    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email_Aluno']
        msg['Subject'] = "Reserva Confirmada - TENNIS CLASS"
        corpo = f"Olá {dados['Aluno']},\n\nReserva confirmada!\nLocal: {dados['Academia']}\nData: {dados['Data']} às {dados['Horario']}\nServiço: {dados['Servico']}"
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# 5. DESIGN E ESTILO (CSS Corrigido - Sem strings abertas)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .custom-card { background-color: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 20px; color: #333; }
    .translucent-balloon { background-color: rgba(60, 60, 60, 0.85); padding: 25px; border-radius: 15px; color: white; backdrop-filter: blur(10px); }
    .btn-cadastro { display: block; width: 100%; background-color: #1e5e20; color: white !important; padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 6. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True): st.session_state.pagina = "Home"
    if st.button("Serviços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 7. LÓGICA DAS PÁGINAS (Corrigindo Indentações e Syntax)
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"):
            st.subheader("📅 Agendamento de Aula")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail para Confirmação")
            servico = st.selectbox("Escolha o Serviço", [
                "Aula Individual R$ 250/hora", "Aula em Grupo R$ 200/hora", 
                "Aula Kids R$ 200/hora", "Treinamento Competitivo R$ 1.200/mês"
            ])
            local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Fontes & Barbeta", "Arena BTG"])
            data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%Y-%m-%d"), "Horario": hora_aula,
                        "Aluno": aluno, "Servico": servico, "Status": "Pendente",
                        "Academia": local, "Email_Aluno": email
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
    else:
        st.subheader("💳 Pagamento via PIX")
        st.info(f"Aluno: {st.session_state.reserva_temp['Aluno']}")
        st.warning("Chave PIX: aranha.corp@gmail.com")
        if st.button("CONFIRMAR AGENDAMENTO FINAL"):
            try:
                # Gravação na Planilha com Parênteses Fechados
                df_existente = conn.read(worksheet="Página1")
                df_novo = pd.concat([df_existente, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo)
                enviar_confirmacao(st.session_state.reserva_temp)
                st.success("Salvo com sucesso na TennisClass_DB!")
                st.balloons()
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro na gravação: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="translucent-balloon"><h3>📝 Portal de Cadastros</h3>', unsafe_allow_html=True)
    #
