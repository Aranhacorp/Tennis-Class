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
        senha = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class"
        corpo = f"Olá {dados['Aluno']},\n\nSua reserva foi confirmada!\n\nDetalhes:\n📅 Data: {dados['Data']}\n⏰ Hora: {dados['Hora']}\n📍 Local: {dados['Local']}\n🎾 Serviço: {dados['Servico']}\n\nAté logo!"
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
    .contact-balloon {
        background-color: rgba(128, 128, 128, 0.4);
        padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2);
        color: white; backdrop-filter: blur(5px);
    }
    .sidebar-title { color: white; font-weight: bold; font-size: 18px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("### 🎾 MENU")
    if st.button("Home (Reservas)", use_container_width=True): 
        st.session_state.pagina = "Home"
        st.session_state.pagamento = False
    if st.button("Serviços & Preços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Produtos", use_container_width=True): st.session_state.pagina = "Produtos"
    if st.button("Cadastros Oficiais", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"
    st.markdown("---")
    st.markdown('<p class="sidebar-title">🏢 Academias</p>', unsafe_allow_html=True)
    st.info("📍 Play Tennis Ibirapuera\n\n📍 Top One Tennis\n\n📍 Fontes & Barbeta\n\n📍 Arena BTG")

# 6. PÁGINAS

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
                serv = st.selectbox("Escolha o Serviço", [
                    "Aula Individual (R$ 250/hora)", 
                    "Aula em Grupo (R$ 200/hora)", 
                    "Aula Kids (R$ 200/hora)", 
                    "Treinamento Esportivo (R$ 1.200/mês)", 
                    "Eventos (A combinar)"
                ])
                local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Arena BTG", "Fontes & Barbeta"])
                dt = st.date_input("Data", format="DD/MM/YYYY")
                hr = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
                if st.form_submit_button("RESERVAR E IR PARA PAGAMENTO"):
                    if nome and email:
                        st.session_state.reserva = {"Aluno": nome, "Email": email, "Servico": serv, "Local": local, "Data": dt.strftime("%d/%m/%Y"), "Hora": hr}
                        st.session_state.pagamento = True
                        st.rerun()
                    else: st.error("Preencha os campos obrigatórios.")
        else:
            st.markdown(f"### 💳 Pagamento PIX: {st.session_state.reserva['Aluno']}")
            st.code("aranha.corp@gmail.com.br", language="text")
            if st.button("CONFIRMAR E ENVIAR E-MAIL"):
                enviar_confirmacao(st.session_state.reserva)
                try:
                    df_nova = pd.DataFrame([st.session_state.reserva])
                    conn.create(data=df_nova)
                except: pass
                st.success("Reserva finalizada!")
                st.balloons()
                st.session_state.pagamento = False
        st.markdown('</div>', unsafe_allow_html=True)

# SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="main-card"><h2>🎾 Tabela de Preços</h2>'
                '<ul><li><b>Individual:</b> R$ 250/h</li><li><b>Grupo/Kids:</b> R$ 200/h</li>'
                '<li><b>Treinamento:</b> R$ 1.200/mês (2h/sem)</li><li><b>Eventos:</b> Sob consulta</li></ul></div>', unsafe_allow_html=True)

# CADASTRO (FORMS ATUALIZADOS)
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="main-card"><h2>📝 Cadastros Oficiais</h2>', unsafe_allow_html=True)
    st.link_button("👤 Cadastro de Aluno", "https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform")
    st.link_button("🏢 Cadastro de Academia", "https://docs.google.com/forms/d/e/1FAIpQLScyM6VvP0n_M0zIe-W_XzVw_v_v_v/viewform") # Link exemplo para academia
    st.link_button("🎾 Cadastro de Professor", "https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform")
    st.markdown('</div>', unsafe_allow_html=True)

# CONTATO (BALÃO CINZA TRANSPARENTE)
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="contact-balloon">'
                '<h2>📩 Fale Conosco</h2>'
                '<p><b>WhatsApp:</b> (11) 97142-5028</p>'
                '<p><b>E-mail:</b> aranha.corp@gmail.com.br</p>'
                '<p><b>Instagram:</b> @tennisclass_</p>'
                '</div>', unsafe_allow_html=True)

# PRODUTOS
elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="main-card"><h2>🎒 Loja</h2><p>Em breve!</p></div>', unsafe_allow_html=True)
