import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide", page_icon="🎾")

# 2. CONEXÃO COM O BANCO DE DADOS (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CONTROLE DE ESTADO DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'inicio_timer' not in st.session_state: st.session_state.inicio_timer = None
if 'admin_autenticado' not in st.session_state: st.session_state.admin_autenticado = False

# 4. ESTILIZAÇÃO CSS E COMPONENTES FIXOS
st.markdown("""
<style>
    /* Fundo do App */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }
    .custom-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: #333; }
    .translucent-balloon { background-color: rgba(50, 50, 50, 0.85); padding: 25px; border-radius: 15px; color: white; backdrop-filter: blur(10px); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
    
    /* Portal de Cadastros Clean */
    .btn-cadastro-clean {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background-color: rgba(30, 100, 30, 0.9);
        color: white !important; text-decoration: none; font-weight: bold; text-align: center;
        transition: 0.3s; padding: 20px; border-radius: 15px; border: 2px solid #4CAF50;
        height: 180px; width: 100%;
    }
    .btn-cadastro-clean:hover { transform: scale(1.05); background-color: #4CAF50 !important; }
    .icon-large { font-size: 50px; margin-bottom: 10px; }
    
    /* WhatsApp Flutuante */
    .whatsapp-float {
        position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px;
        background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center;
        font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 9999;
        display: flex; align-items: center; justify-content: center; text-decoration: none;
    }
    
    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; opacity: 0.8; }
</style>

<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35">
</a>

<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
""", unsafe_allow_html=True)

# 5. NAVEGAÇÃO LATERAL (MENU)
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    menu = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    for opcao in menu:
        if st.button(opcao, key=f"btn_{opcao}", use_container_width=True):
            st.session_state.pagina = opcao
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏢 Academias Parceiras")
    academias_info = {
        "PLAY TENNIS Ibirapuera": "R. Estado de Israel, 860 - SP",
        "TOP One Tennis": "Unidade Premium",
        "MELL Tennis": "Unidade Zona Sul",
        "ARENA BTG Morumbi": "Unidade Morumbi"
    }
    for nome, endereco in academias_info.items():
        st.markdown(f"📍 **{nome}**\n\n<div style='font-size: 12px; color: #ccc;'>{endereco}</div>", unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DE PÁGINAS
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
                "Treinamento competitivo R$ 1.400/mes"
            ])
            local = st.selectbox("Unidade", list(academias_info.keys()))
            
            c1, c2 = st.columns(2)
            with c1: data_aula = st.date_input("Data", format="DD/MM/YYYY")
            with c2: horario_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 23)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%d/%m/%Y"), "Horário": horario_aula,
                        "Aluno": aluno, "Serviço": servico, "Unidade": local, "Status": "Pendente"
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
    else:
        # PAGAMENTO E CRONÔMETRO
        timer_placeholder = st.empty()
        st.subheader("💳 Pagamento via PIX")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com")
        st.info("Chave PIX: aranha.corp@gmail.com")
        
        if st.button("CONFIRMAR PAGAMENTO", type="primary"):
            try:
                df = conn.read(worksheet="Página1")
                df_novo = pd.concat([df, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo)
                st.success("Reserva Confirmada!")
                st.balloons()
                st.session_state.pagamento_ativo = False
                time.sleep(2)
                st.rerun()
            except Exception as e: st.error(f"Erro: {e}")

        while st.session_state.pagamento_ativo:
            restante = 300 - (time.time() - st.session_state.inicio_timer)
            if restante <= 0:
                st.session_state.pagamento_ativo = False
                st.rerun()
            m, s = divmod(int(restante), 60)
            timer_placeholder.error(f"⏱️ Tempo restante para o PIX: {m:02d}:{s:02d}")
            time.sleep(1)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Preços":
    # TABELA DE PREÇOS RESTAURADA
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.markdown("### 🎾 Tabela de Preços")
    st.markdown("---")
    st.write("• **Individual:** R$ 250/h")
    st.write("• **Grupo/Kids:** R$ 200/h")
    st.write("• **Treinamento competitivo:** R$ 1.400 / mês (8 horas de treino)")
    st.write("• **Eventos:** Sob consulta")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    # PORTAL DE CADASTROS
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSd7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform" class="btn-cadastro-clean" target="_blank"><div class="icon-large">👤</div>Aluno</a>', unsafe_allow_html=True)
    with col2:
        st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro-clean" target="_blank"><div class="icon-large">🏢</div>Academia</a>', unsafe_allow_html=True)
    with col3:
        st.markdown('<a href="https://docs.google.com/forms/d/1q4HQq9uY1ju2ZsgOcFb7BF0LtKstpe3fYwjur4WwMLY/viewform" class="btn-cadastro-clean" target="_blank"><div class="icon-large">🎾</div>Professor</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Dashboard":
    # ADMINISTRAÇÃO
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("📊 Administração")
    if not st.session_state.admin_autenticado:
        senha = st.text_input("Chave de Acesso", type="password")
        if st.button("Acessar"):
            if senha == "aranha2026":
                st.session_state.admin_autenticado = True
                st.rerun()
            else: st.error("Acesso Negado")
    else:
        dados = conn.read(worksheet="Página1")
        st.dataframe(dados, use_container_width=True)
        if st.button("Logout"):
            st.session_state.admin_autenticado = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    # CONTATO
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📞 Canais de Atendimento")
    st.write("📧 **E-mail:** aranha.corp@gmail.com")
    st.write("📱 **WhatsApp:** (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)
