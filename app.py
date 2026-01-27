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
        senha = st.secrets["EMAIL_PASSWORD"] # Utiliza 'xmtw pnyq wsav iock'
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class"
        corpo = f"Olá {dados['Aluno']},\n\nSua reserva foi confirmada!\n\n📅 Data: {dados['Data']}\n⏰ Hora: {dados['Hora']}\n📍 Local: {dados['Local']}\n🎾 Serviço: {dados['Servico']}\n\nAté logo!"
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

# 4. ESTILIZAÇÃO CSS (Balões cinzas com transparência)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-attachment: fixed;
    }
    .translucent-balloon {
        background-color: rgba(60, 60, 60, 0.6);
        padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
        color: white; backdrop-filter: blur(8px); margin-bottom: 20px;
    }
    .main-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: black; }
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

# HOME / RESERVAS (Mantendo formulário branco para leitura fácil)
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
                    else: st.error("Preencha os campos.")
        else:
            st.markdown(f"### 💳 PIX: {st.session_state.reserva['Aluno']}")
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

# SERVIÇOS (Balão Transparente)
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="translucent-balloon"><h2>🎾 Serviços e Valores</h2>'
                '<ul><li><b>Aula Individual:</b> R$ 250/hora</li>'
                '<li><b>Aula em Grupo:</b> R$ 200/hora</li>'
                '<li><b>Aula Kids:</b> R$ 200/hora</li>'
                '<li><b>Treinamento Esportivo:</b> R$ 1.200/mês (2h por semana)</li>'
                '<li><b>Eventos:</b> Valor a combinar</li></ul></div>', unsafe_allow_html=True)

# PRODUTOS (Balão Transparente)
elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="translucent-balloon"><h2>🎒 Loja Tennis Class</h2>'
                '<p>Nossa linha exclusiva de vestuário e equipamentos está em fase de lançamento.</p>'
