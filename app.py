import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# --- 2. FUNÇÃO DE ENVIO DE E-MAIL ---
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
        
        Nos vemos na quadra!
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

# --- 3. ESTADOS DA SESSÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento' not in st.session_state: st.session_state.pagamento = False

# --- 4. CSS E ESTILIZAÇÃO ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-attachment: fixed;
    }
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px; border-radius: 20px; color: black;
    }
    .sidebar-title { color: white; font-weight: bold; font-size: 18px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 5. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🎾 MENU")
    if st.button("Home", use_container_width=True): 
        st.session_state.pagina = "Home"
        st.session_state.pagamento = False
    if st.button("Serviços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Produtos", use_container_width=True): st.session_state.pagina = "Produtos"
    if st.button("Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"
    
    st.markdown("---")
    st.markdown('<p class="sidebar-title">🏢 Academias</p>', unsafe_allow_html=True)
    st.button("📍 Play Tennis Ibirapuera", use_container_width=True)
    st.button("📍 Top One Tennis", use_container_width=True)
    st.button("📍 Fontes & Barbeta Tennis", use_container_width=True)
    st.button("📍 Arena BTG", use_container_width=True)

# --- 6. LÓGICA DAS PÁGINAS ---

# PÁGINA HOME (RESERVAS)
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align:center; color:white;'>TENNIS CLASS</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if not st.session_state.pagamento:
            with st.form("reserva_form"):
                st.subheader("📅 Agendamento de Aula")
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome do Aluno")
                    email = st.text_input("E-mail para Confirmação")
                with col2:
                    serv = st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Aulas em Grupo", "Aulas Kids"])
                    local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Arena BTG"])
                
                dt = st.date_input("Data da Aula", format="DD/MM/YYYY")
                hr = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
                
                if st.form_submit_button("RESERVAR E IR PARA PAGAMENTO"):
                    if nome and email:
                        st.session_state.reserva = {
                            "Aluno": nome, "Email": email, "Servico": serv, 
                            "Local": local, "Data": dt.strftime("%d/%m/%Y"), "Hora": hr
                        }
                        st.session_state.pagamento = True
                        st.rerun()
                    else: st.error("Por favor, preencha nome e e-mail.")
        else:
            st.markdown(f"### Pagamento PIX para {st.session_state.reserva['Aluno']}")
            st.write("Chave: **aranha.corp@gmail.com.br**")
            if st.button("CONFIRMAR E ENVIAR E-MAIL"):
                if enviar_confirmacao(st.session_state.reserva):
                    st.success("Reserva confirmada e e-mail enviado!")
                    st.balloons()
                else:
                    st.warning("Reserva salva, mas verifique os Secrets para o envio do e-mail.")
                st.session_state.pagamento = False
        st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 🎾 Nossos Serviços")
    st.write("Aulas particulares, em grupo e clínicas especializadas.")
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA PRODUTOS
elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 🎒 Produtos")
    st.write("Equipamentos e acessórios oficiais Tennis Class.")
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA CADASTRO (LINKS GOOGLE FORMS)
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 📝 Cadastros Oficiais")
    st.link_button("👤 Cadastro de Aluno", "https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform")
    st.link_button("🎾 Cadastro de Professor", "https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform")
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 📩 Contato")
    st.write("WhatsApp: (11) 97142-5028")
    st.write("E-mail: aranha.corp@gmail.com.br")
    st.markdown('</div>', unsafe_allow_html=True)
