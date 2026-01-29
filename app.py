import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

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

# 4. DESIGN CSS (Visual Clean e Premium)
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
    
    /* Cadastro: Apenas ícones e nomes */
    .btn-cadastro-clean {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        color: white !important; text-decoration: none; font-weight: bold; text-align: center;
        transition: 0.3s; padding: 10px;
    }
    .btn-cadastro-clean:hover { transform: scale(1.15); color: #4CAF50 !important; }
    .icon-large { font-size: 90px; margin-bottom: 10px; }
    
    /* WhatsApp Flutuante */
    .whatsapp-float {
        position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px;
        background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center;
        font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 1000;
        display: flex; align-items: center; justify-content: center;
    }

    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .sidebar-detalhe { font-size: 12px; color: #ccc; padding-left: 20px; margin-bottom: 10px; }
</style>

<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="40">
</a>

<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    menu = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    for item in menu:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏢 Academias")
    academias = {
        "PLAY TENNIS Ibirapuera": "R. Estado de Israel, 860 - SP",
        "TOP One Tennis": "Unidade Premium",
        "MELL Tennis": "Unidade Zona Sul",
        "ARENA BTG Morumbi": "Unidade Morumbi"
    }
    for nome, info in academias.items():
        st.markdown(f"📍 **{nome}**")
        st.markdown(f'<div class="sidebar-detalhe">{info}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"):
            st.subheader("📅 Agendar Aula")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail para Confirmação")
            servico = st.selectbox("Serviço", ["Aulas particulares R$ 250/hora", "Aulas em Grupo R$ 200/hora", "Treinamento competitivo R$ 1.400/mes"])
            local = st.selectbox("Unidade", list(academias.keys()))
            c1, c2 = st.columns(2)
            with c1: data_aula = st.date_input("Data", format="DD/MM/
