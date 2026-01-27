import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_email_confirmacao(dados):
    try:
        remetente = "aranha.corp@gmail.com.br"
        # Puxa a senha que você salvou nos Secrets
        senha = st.secrets["EMAIL_PASSWORD"] 
        
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - {dados['Aluno']}"
        
        corpo = f"""
        Olá {dados['Aluno']}, sua reserva na Tennis Class foi confirmada!
        
        DETALHES DA RESERVA:
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
        # Envia para o aluno e uma cópia para você
        server.sendmail(remetente, [dados['Email'], remetente], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# 2. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_pendente' not in st.session_state: st.session_state.pagamento_pendente = False

# 3. DESIGN E INTERFACE
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
    }
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px; border-radius: 20px; color: black; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 4. NAVEGAÇÃO LATERAL
with st.sidebar:
    st.markdown("### 🎾 TENNIS CLASS")
    if st.button("Página de Reservas", use_container_width=True):
        st.session_state.pagina = "Home"
        st.session_state.pagamento_pendente = False
    if st.button("Cadastros Oficiais", use_container_width=True):
        st.session_state.pagina = "Cadastro"

# 5. LÓGICA DA PÁGINA DE RESERVAS
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align:center; color:white;'>TENNIS CLASS</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if not st.session_state.pagamento_pendente:
            with st.form("form_reserva"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_aluno = st.text_input("Nome do Aluno")
                    email_aluno = st.text_input("E-mail para Confirmação")
                with col2:
                    servico = st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Aulas em Grupo", "Aulas Kids"])
                    local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Arena BTG"])
                
                data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
                
                if st.form_submit_button("RESERVAR E IR PARA PAGAMENTO"):
                    if nome_aluno and email_aluno:
                        st.session_state.dados_reserva = {
                            "Aluno": nome_aluno, "Email": email_aluno, "Servico": servico, 
                            "Local": local, "Data": data_aula.strftime("%d/%m/%Y"), "Hora": horario
                        }
                        st.session_state.pagamento_pendente = True
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o Nome e o E-mail.")
        else:
            st.markdown(f"### Quase lá, {st.session_state.dados_reserva['Aluno']}!")
            st.write("Realize o PIX para: **aranha.corp@gmail.com.br**")
            st.write("Após o pagamento, clique no botão abaixo para receber sua confirmação.")
            if st.button("CONFIRMAR AGENDAMENTO"):
                if enviar_email_confirmacao(st.session_state.dados_reserva):
                    st.success("Tudo certo! Verifique sua caixa de entrada.")
                    st.balloons()
                else:
                    st.warning("Reserva confirmada! (Ocorreu um problema técnico no envio do e-mail, verifique os Secrets).")
                st.session_state.pagamento_pendente = False
        st.markdown('</div>', unsafe_allow_html=True)

# 6. PÁGINA DE CADASTROS (LINKS GOOGLE FORMS)
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Portal de Cadastros")
    st.link_button("👤 Cadastro de Aluno", "https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform")
    st.link_button("🎾 Cadastro de Professor", "https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform")
    st.markdown('</div>', unsafe_allow_html=True)
