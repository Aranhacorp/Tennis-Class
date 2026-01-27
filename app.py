import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM GOOGLE SHEETS (Puxa os dados do seu Secrets [connections.gsheets])
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro na conexão com a planilha. Verifique o Secrets.")

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_confirmacao(dados):
    try:
        remetente = "aranha.corp@gmail.com.br"
        # Puxa a senha 'xmtw pnyq wsav iock' do seu Secrets
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

# 3. ESTADOS DA SESSÃO (Para navegação e fluxo de pagamento)
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento' not in st.session_state: st.session_state.pagamento = False

# 4. ESTILIZAÇÃO E FUNDO
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

# 5. MENU LATERAL (RESTAURADO)
with st.sidebar:
    st.markdown("### 🎾 MENU")
    if st.button("Home (Reservas)", use_container_width=True): 
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
    st.button("📍 Fontes & Barbeta", use_container_width=True)
    st.button("📍 Arena BTG", use_container_width=True)

# 6. PÁGINAS DO APLICATIVO

# HOME / RESERVAS
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align:center; color:white;'>TENNIS CLASS</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if not st.session_state.pagamento:
            with st.form("reserva_form"):
                st.subheader("📅 Agendamento")
                nome = st.text_input("Nome do Aluno")
                email = st.text_input("E-mail")
                serv = st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Aulas em Grupo", "Kids"])
                local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Arena BTG"])
                dt = st.date_input("Data", format="DD/MM/YYYY")
                hr = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
                
                if st.form_submit_button("RESERVAR E IR PARA PAGAMENTO"):
                    if nome and email:
                        st.session_state.reserva = {"Aluno": nome, "Email": email, "Servico": serv, "Local": local, "Data": dt.strftime("%d/%m/%Y"), "Hora": hr}
                        st.session_state.pagamento = True
                        st.rerun()
                    else: st.error("Preencha todos os campos.")
        else:
            st.markdown(f"### Pagamento PIX para {st.session_state.reserva['Aluno']}")
            st.code("aranha.corp@gmail.com.br", language="text")
            if st.button("CONFIRMAR E FINALIZAR"):
                # 1. Enviar E-mail
                sucesso_email = enviar_confirmacao(st.session_state.reserva)
                # 2. Salvar na Planilha
                try:
                    df_nova = pd.DataFrame([st.session_state.reserva])
                    conn.create(data=df_nova) # Adiciona na planilha do Secrets
                    st.success("Reserva salva na planilha!")
                except:
                    st.info("Reserva concluída (Erro ao gravar na planilha).")
                
                if sucesso_email: st.success("E-mail de confirmação enviado!")
                st.balloons()
                st.session_state.pagamento = False
        st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="main-card"><h2>🎾 Serviços</h2><p>Aulas individuais e clínicas.</p></div>', unsafe_allow_html=True)

# PÁGINA PRODUTOS
elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="main-card"><h2>🎒 Loja</h2><p>Em breve!</p></div>', unsafe_allow_html=True)

# PÁGINA CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="main-card"><h2>📝 Cadastros</h2>', unsafe_allow_html=True)
    st.link_button("👤 Aluno", "https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform")
    st.link_button("🎾 Professor", "https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform")
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="main-card"><h2>📩 Contato</h2><p>WhatsApp: (11) 97142-5028</p></div>', unsafe_allow_html=True)
