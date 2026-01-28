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
if 'admin_autenticado' not in st.session_state: st.session_state.admin_autenticado = False

# 4. FUNÇÃO DE ENVIO DE E-MAIL
def enviar_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" 
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

# 5. DESIGN, CSS E ELEMENTOS FLUTUANTES
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
    
    .btn-cadastro-horiz {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background-color: #1e5e20; color: white !important; padding: 20px; border-radius: 15px;
        text-decoration: none; font-weight: bold; text-align: center; transition: 0.3s; height: 150px;
    }
    .btn-cadastro-horiz:hover { background-color: #2e7d32; transform: translateY(-5px); }
    .icon-cadastro { font-size: 40px; margin-bottom: 10px; }

    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-footer { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; transition: 0.3s; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-footer">
</a>
""", unsafe_allow_html=True)

# 6. MENU LATERAL
info_academias = {
    "PLAY TENNIS Ibirapuera": "R. Estado de Israel, 860 - SP",
    "TOP One Tennis": "Av. Indianópolis, 647 - SP",
    "MELL Tennis": "Rua Oscar Gomes Cardim, 535 - SP",
    "ARENA BTG Morumbi": "Av. Major Sylvio de Magalhães Padilha, 16741 - SP"
}

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
    for nome in info_academias.keys():
        if st.button(f"📍 {nome}", key=f"side_{nome}", use_container_width=True):
            st.session_state.academia_foco = nome if st.session_state.academia_foco != nome else None
        if st.session_state.academia_foco == nome:
            st.markdown(f'<div style="color:white; padding-left:20px;">{info_academias[nome]}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 7. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"):
            st.subheader("📅 Agendar Aula")
            aluno, email = st.text_input("Nome"), st.text_input("E-mail")
            servico = st.selectbox("Serviço", ["Aula Individual (R$ 250/h)", "Aula em Grupo (R$ 200/h)", "Aula Kids (R$ 200/h)", "Treinamento competitivo: R$ 1.400 / mês (8 horas de treino)"])
            local = st.selectbox("Unidade", list(info_academias.keys()))
            data_aula = st.date_input("Data", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {"Data": str(data_aula), "Horario": hora_aula, "Aluno": aluno, "Servico": servico, "Status": "Pendente", "Academia": local, "Email_Aluno": email}
                    st.session_state.pagamento_ativo = True
                    st.rerun()
    else:
        st.subheader("💳 Pagamento via PIX")
        st.info("Chave PIX: aranha.corp@gmail.com")
        if st.button("CONFIRMAR AGENDAMENTO"):
            try:
                df = conn.read(worksheet="Página1")
                df_novo = pd.concat([df, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo)
                enviar_confirmacao(st.session_state.reserva_temp)
                st.success("Sucesso! E-mail enviado.")
                st.balloons()
                st.session_state.pagamento_ativo = False
            except Exception as e: st.error(f"Erro: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.markdown("## 🎾 Tabela de Preços")
    st.write("- Individual: R$ 250/h\n- Grupo/Kids: R$ 200/h")
    st.write("- **Treinamento competitivo: R$ 1.400 / mês (8 horas de treino)**")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros")
    c1, c2, c3 = st.columns(3)
    links = [
        ("https://docs.google.com/forms/d/e/1FAIpQLSd7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform", "👤 Aluno"),
        ("https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform", "🏢 Academia"),
        ("https://docs.google.com/forms/d/1q4HQq9uY1ju2ZsgOcFb7BF0LtKstpe3fYwjur4WwMLY/viewform", "🎾 Professor")
    ]
    for col, (link, label) in zip([c1, c2, c3], links):
        col.markdown(f'<a href="{link}" class="btn-cadastro-horiz"><div class="icon-cadastro">{label.split()[0]}</div>{label}</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("📊 Painel Administrativo")
    if not st.session_state.admin_autenticado:
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar"):
            if senha == "aranha2026": 
                st.session_state.admin_autenticado = True
                st.rerun()
            else: st.error("Senha incorreta!")
    else:
        if st.button("Sair do Painel"):
            st.session_state.admin_autenticado = False
            st.rerun()
        df_dash = conn.read(worksheet="Página1")
        st.write(f"Total de Agendamentos: **{len(df_dash)}**")
        st.dataframe(df_dash, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="translucent-balloon">📩 aranha.corp@gmail.com <br> 📱 (11) 97142-5028</div>', unsafe_allow_html=True)
