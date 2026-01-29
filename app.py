import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide", page_icon="🎾")

# 2. CONEXÃO COM A PLANILHA
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'inicio_timer' not in st.session_state: st.session_state.inicio_timer = None
if 'admin_autenticado' not in st.session_state: st.session_state.admin_autenticado = False

# 4. FUNÇÃO DE ENVIO DE E-MAIL
def enviar_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" 
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = remetente, dados['Email_Aluno']
        msg['Subject'] = "Reserva Confirmada - TENNIS CLASS"
        corpo = f"Olá {dados['Aluno']},\n\nSua reserva foi confirmada!\nLocal: {dados['Academia']}\nServiço: {dados['Servico']}"
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# 5. DESIGN E CSS (Revisado para evitar duplicidade e erros de string)
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
    
    .btn-cadastro-single {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background-color: #1e5e20; color: white !important; padding: 25px; border-radius: 15px;
        text-decoration: none; font-weight: bold; text-align: center; transition: 0.3s; height: 180px;
        border: 2px solid rgba(255,255,255,0.1);
    }
    .btn-cadastro-single:hover { background-color: #2e7d32; transform: scale(1.05); }
    .icon-box { font-size: 60px; margin-bottom: 10px; }
    
    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-footer { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-footer">
</a>
""", unsafe_allow_html=True)

# 6. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False # Reseta fluxo se mudar de aba
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 7. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"):
            st.subheader("📅 Agendar Aula")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail para Confirmação")
            servico = st.selectbox("Escolha o Serviço", [
                "Aulas particulares R$ 250/hora", 
                "Aulas em Grupo R$ 200/hora", 
                "Aula Kids R$ 200/hora", 
                "Treinamento competitivo R$ 1.400/mes", 
                "Eventos valor a combinar"
            ])
            local = st.selectbox("Unidade", ["PLAY TENNIS Ibirapuera", "TOP One Tennis", "MELL Tennis", "ARENA BTG Morumbi"])
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {"Aluno": aluno, "Servico": servico, "Academia": local, "Email_Aluno": email}
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else: st.warning("Preencha todos os campos!")
    else:
        # LÓGICA DO TIMER (5 MINUTOS)
        passado = time.time() - st.session_state.inicio_timer
        restante = 300 - passado
        if restante <= 0:
            st.error("Tempo esgotado! Inicie o agendamento novamente.")
            st.session_state.pagamento_ativo = False
            time.sleep(2)
            st.rerun()
        
        mins, secs = divmod(int(restante), 60)
        st.error(f"⏱️ Tempo restante para o PIX: {mins:02d}:{secs:02d}")
        
        st.subheader("💳 Pagamento via PIX")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com", caption="Escaneie para Pagar")
        st.info(f"Chave PIX: aranha.corp@gmail.com")
        st.code("aranha.corp@gmail.com", language="text")
        
        if st.button("CONFIRMAR AGENDAMENTO"):
            try:
                df = conn.read(worksheet="Página1")
                df_novo = pd.concat([df, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo)
                enviar_confirmacao(st.session_state.reserva_temp)
                st.success("Tudo pronto! Agendamento confirmado e e-mail enviado.")
                st.balloons()
                st.session_state.pagamento_ativo = False
            except Exception as e: st.error(f"Erro ao salvar: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Preços":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.markdown("## 💰 Tabela de Preços")
    st.write("• **Aulas particulares:** R$ 250/hora")
    st.write("• **Aulas em Grupo:** R$ 200/hora")
    st.write("• **Aula Kids:** R$ 200/hora")
    st.write("• **Treinamento competitivo:** R$ 1.400/mes")
    st.write("• **Eventos:** Valor a combinar")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros")
    # APENAS 3 COLUNAS, 1 ÍCONE POR CADASTRO
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSd7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform" class="btn-cadastro-single"><div class="icon-box">👤</div>Aluno</a>', unsafe_allow_html=True)
    with col2:
        st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro-single"><div class="icon-box">🏢</div>Academia</a>', unsafe_allow_html=True)
    with col3:
        st.markdown('<a href="https://docs.google.com/forms/d/1q4HQq9uY1ju2ZsgOcFb7BF0LtKstpe3fYwjur4WwMLY/viewform" class="btn-cadastro-single"><div class="icon-box">🎾</div>Professor</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.admin_autenticado:
        senha = st.text_input("Acesso Restrito", type="password")
        if st.button("Entrar"):
            if senha == "aranha2026": 
                st.session_state.admin_autenticado = True
                st.rerun()
            else: st.error("Senha inválida!")
    else:
        st.subheader("📊 Relatório de Agendamentos")
        df_dash = conn.read(worksheet="Página1")
        st.dataframe(df_dash, use_container_width=True)
        if st.button("Logout"): st.session_state.admin_autenticado = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="translucent-balloon">📞 (11) 97142-5028 <br> 📩 aranha.corp@gmail.com</div>', unsafe_allow_html=True)
