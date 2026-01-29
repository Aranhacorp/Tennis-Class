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
    
    /* Portal de Cadastros Clean: Apenas ícones e nomes */
    .btn-cadastro-clean {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background-color: rgba(30, 100, 30, 0.9); /* Verde Tênis Escuro */
        color: white !important; text-decoration: none; font-weight: bold; text-align: center;
        transition: 0.3s; padding: 20px; border-radius: 15px; border: 2px solid #4CAF50;
        height: 180px; width: 100%;
    }
    .btn-cadastro-clean:hover { transform: scale(1.05); background-color: #4CAF50 !important; color: white !important; }
    .icon-large { font-size: 50px; margin-bottom: 10px; }
    
    /* WhatsApp Flutuante Corrigido */
    .whatsapp-float {
        position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px;
        background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center;
        font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 9999;
        display: flex; align-items: center; justify-content: center; text-decoration: none;
    }
    
    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; opacity: 0.8; }
    .sidebar-detalhe { font-size: 12px; color: #ccc; margin-bottom: 10px; }
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
        st.markdown(f"📍 **{nome}**")
        st.markdown(f'<div class="sidebar-detalhe">{endereco}</div>', unsafe_allow_html=True)

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
                    st.warning("Preencha nome e e-mail.")
    else:
        # CRONÔMETRO DE PAGAMENTO
        timer_placeholder = st.empty()
        st.subheader("💳 Pagamento via PIX")
        c1, c2 = st.columns([1,2])
        with c1:
            st.image("https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com")
        with c2:
            st.info("Chave PIX: aranha.corp@gmail.com")
            st.write("Após o pagamento, clique em confirmar abaixo.")
        
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
            except Exception as e: 
                st.error(f"Erro ao registrar: {e}")

        while st.session_state.pagamento_ativo:
            restante = 300 - (time.time() - st.session_state.inicio_timer)
            if restante <= 0:
                st.session_state.pagamento_ativo = False
                st.rerun()
            m, s = divmod(int(restante), 6
