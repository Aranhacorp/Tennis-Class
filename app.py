import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

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

# 4. DESIGN CSS
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
        text-decoration: none; font-weight: bold; text-align: center; height: 180px;
    }
    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"):
            st.subheader("📅 Agendar Aula")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail para Confirmação")
            servico = st.selectbox("Escolha o Serviço", ["Aulas particulares R$ 250/hora", "Aulas em Grupo R$ 200/hora", "Aula Kids R$ 200/hora", "Treinamento competitivo R$ 1.400/mes"])
            local = st.selectbox("Unidade", ["PLAY TENNIS Ibirapuera", "TOP One Tennis", "MELL Tennis", "ARENA BTG Morumbi"])
            
            col_d, col_h = st.columns(2)
            with col_d: data_aula = st.date_input("Data", format="DD/MM/YYYY")
            with col_h: 
                # HORÁRIO DE HORA EM HORA
                lista_horas = [f"{h:02d}:00" for h in range(7, 23)]
                horario_aula = st.selectbox("Horário", lista_horas)
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%d/%m/%Y"), "Horário": horario_aula,
                        "Aluno": aluno, "Serviço": servico, "Status": "Pendente", "Unidade": local, "Email": email
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
    else:
        # CRONÔMETRO REGRESSIVO DINÂMICO
        timer_placeholder = st.empty()
        st.subheader("💳 Pagamento via PIX")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com")
        st.code("aranha.corp@gmail.com", language="text")
        
        btn_confirmar = st.button("CONFIRMAR PAGAMENTO")
        
        # Loop do cronômetro
        while st.session_state.pagamento_ativo:
            restante = 300 - (time.time() - st.session_state.inicio_timer)
            if restante <= 0:
                st.session_state.pagamento_ativo = False
                st.error("Tempo esgotado! Tente novamente.")
                time.sleep(2)
                st.rerun()
                break
            
            mins, secs = divmod(int(restante), 60)
            timer_placeholder.error(f"⏱️ Tempo restante para o PIX: {mins:02d}:{secs:02d}")
            
            if btn_confirmar:
                try:
                    df = conn.read(worksheet="Página1")
                    df_novo = pd.concat([df, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_novo)
                    st.success("Reserva confirmada!")
                    st.balloons()
                    st.session_state.pagamento_ativo = False
                    time.sleep(3)
                    st.rerun()
                except: st.error("Erro ao salvar no Banco de Dados.")
            
            time.sleep(1) # Atualiza a cada 1 segundo
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Preços":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.markdown("## 💰 Tabela de Preços")
    st.write("• **Individual:** R$ 250/h | **Grupo/Kids:** R$ 200/h")
    st.write("• **Treinamento competitivo:** R$ 1.400 / mês (8 horas de treino)")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros")
    c1, c2, c3 = st.columns(3) # Apenas 3 ícones no total
    with c1: st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSd7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform" class="btn-cadastro-single"><div style="font-size:50px">👤</div>Aluno</a>', unsafe_allow_html=True)
    with c2: st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro-single"><div style="font-size:50px">🏢</div>Academia</a>', unsafe_allow_html=True)
    with c3: st.markdown('<a href="https://docs.google.com/forms/d/1q4HQq9uY1ju2ZsgOcFb7BF0LtKstpe3fYwjur4WwMLY/viewform" class="btn-cadastro-single"><div style="font-size:50px">🎾</div>Professor</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    # CONTATO EM BALÃO CINZA TRANSLÚCIDO
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📞 Canais de Atendimento")
    st.write("📧 **E-mail:** aranha.corp@gmail.com")
    st.write("📱 **WhatsApp:** (11) 97142-5028")
    st.write("📍 **Sede:** São Paulo, SP")
    st.markdown('</div>', unsafe_allow_html=True)
