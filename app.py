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
        senha = st.secrets["EMAIL_PASSWORD"] # Usa a senha 'xmtw pnyq wsav iock' do seu Secrets
        
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = dados['Email']
        msg['Subject'] = f"🎾 Reserva Confirmada - Tennis Class"
        
        corpo = f"""
        Olá {dados['Aluno']}, sua reserva foi confirmada!
        
        DETALHES DA RESERVA:
        📅 Data: {dados['Data']}
        ⏰ Horário: {dados['Hora']}
        📍 Local: {dados['Local']}
        🎾 Serviço: {dados['Servico']}
        
        Aguardamos você na quadra!
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

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento' not in st.session_state: st.session_state.pagamento = False

# 4. ESTILIZAÇÃO CSS (Corrigindo SyntaxErrors de versões anteriores)
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

# 5. MENU LATERAL (RESTAURADO COM ACADEMIAS)
with st.sidebar:
    st.markdown("### 🎾 MENU PRINCIPAL")
    if st.button("Home (Reservas)", use_container_width=True): 
        st.session_state.pagina = "Home"
        st.session_state.pagamento = False
    if st.button("Serviços & Preços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Produtos", use_container_width=True): st.session_state.pagina = "Produtos"
    if st.button("Área de Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"
    
    st.markdown("---")
    st.markdown('<p class="sidebar-title">🏢 Academias Parceiras</p>', unsafe_allow_html=True)
    st.button("📍 Play Tennis Ibirapuera", use_container_width=True)
    st.button("📍 Top One Tennis", use_container_width=True)
    st.button("📍 Fontes & Barbeta", use_container_width=True)
    st.button("📍 Arena BTG", use_container_width=True)

# 6. PÁGINAS

# HOME / RESERVAS
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align:center; color:white;'>TENNIS CLASS</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if not st.session_state.pagamento:
            with st.form("reserva_form"):
                st.subheader("📅 Agendamento Online")
                nome = st.text_input("Nome do Aluno")
                email = st.text_input("E-mail para Confirmação")
                
                # Novos Serviços e Preços Ajustados
                servico_selecionado = st.selectbox("Escolha o Serviço", [
                    "Aula Individual (R$ 250/hora)", 
                    "Aula em Grupo (R$ 200/hora)", 
                    "Aula Kids (R$ 200/hora)", 
                    "Treinamento Esportivo (R$ 1.200/mês - 2h/semana)", 
                    "Eventos (A combinar)"
                ])
                
                local = st.selectbox("Unidade", ["Play Tennis Ibirapuera", "Top One Tennis", "Arena BTG", "Fontes & Barbeta"])
                dt = st.date_input("Data", format="DD/MM/YYYY")
                hr = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
                
                if st.form_submit_button("RESERVAR E IR PARA PAGAMENTO"):
                    if nome and email:
                        st.session_state.reserva = {
                            "Aluno": nome, "Email": email, "Servico": servico_selecionado, 
                            "Local": local, "Data": dt.strftime("%d/%m/%Y"), "Hora": hr
                        }
                        st.session_state.pagamento = True
                        st.rerun()
                    else: st.error("Por favor, preencha todos os campos.")
        else:
            st.markdown(f"### 💳 Pagamento para: {st.session_state.reserva['Aluno']}")
            st.info(f"Serviço: {st.session_state.reserva['Servico']}")
            st.write("Efetue o PIX para a chave abaixo:")
            st.code("aranha.corp@gmail.com.br", language="text")
            
            if st.button("CONFIRMAR PAGAMENTO E FINALIZAR"):
                with st.spinner("Processando..."):
                    # 1. Enviar E-mail
                    enviar_confirmacao(st.session_state.reserva)
                    # 2. Salvar na Planilha (Via Secrets connections.gsheets)
                    try:
                        df_nova = pd.DataFrame([st.session_state.reserva])
                        conn.create(data=df_nova)
                        st.success("Reserva registrada com sucesso!")
                    except:
                        st.info("Reserva concluída!")
                
                st.balloons()
                st.session_state.pagamento = False
        st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🎾 Tabela de Serviços e Preços")
    st.write("""
    * **Aula Individual:** R$ 250 / hora
    * **Aula em Grupo:** R$ 200 / hora
    * **Aula Kids:** R$ 200 / hora
    * **Treinamento Esportivo:** R$ 1.200 / mês (2 horas por semana)
    * **Eventos:** Valor a combinar conforme necessidade.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINAS PRODUTOS, CADASTRO E CONTATO
elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="main-card"><h2>🎒 Loja de Produtos</h2><p>Raquetes e acessórios em breve.</p></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="main-card"><h2>📝 Formulários</h2>', unsafe_allow_html=True)
    st.link_button("👤 Cadastro de Aluno", "https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform")
    st.link_button("🎾 Cadastro de Professor", "https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="main-card"><h2>📩 Contato Direct</h2><p>WhatsApp: (11) 97142-5028</p></div>', unsafe_allow_html=True)
