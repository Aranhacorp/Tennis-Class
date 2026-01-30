import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# ------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------
st.set_page_config(
    page_title="TENNIS CLASS",
    layout="wide",
    page_icon="🎾"
)

# ------------------------------------------------------
# 2. CONEXÃO COM BANCO DE DADOS
# ------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

# ------------------------------------------------------
# 3. GERENCIAMENTO DE ESTADO (SESSION STATE)
# ------------------------------------------------------
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}
if 'inicio_timer' not in st.session_state:
    st.session_state.inicio_timer = None
if 'admin_autenticado' not in st.session_state:
    st.session_state.admin_autenticado = False

# ------------------------------------------------------
# 4. CSS GLOBAL E ESTILIZAÇÃO VISUAL
# ------------------------------------------------------
st.markdown("""
<style>
    /* Fundo da Aplicação */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Títulos e Textos */
    .header-title {
        color: white;
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px black;
    }
    
    /* Cartões e Balões */
    .custom-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        color: #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .translucent-balloon {
        background-color: rgba(50, 50, 50, 0.85);
        padding: 25px;
        border-radius: 15px;
        color: white;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Botões de Cadastro (Ícones Grandes) */
    .clean-link {
        text-align: center;
        text-decoration: none !important;
        color: white !important;
        transition: 0.3s;
        display: block;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
    }
    .clean-link:hover {
        transform: translateY(-5px);
        background-color: rgba(255,255,255,0.1);
        border-color: #4CAF50;
    }
    .icon-text { font-size: 60px; margin-bottom: 10px; }
    .label-text { font-size: 18px; font-weight: bold; letter-spacing: 1px; }

    /* Botão Flutuante do WhatsApp */
    .whatsapp-float {
        position: fixed;
        width: 60px;
        height: 60px;
        bottom: 40px;
        right: 40px;
        background-color: #25d366;
        color: #FFF;
        border-radius: 50px;
        text-align: center;
        font-size: 35px;
        box-shadow: 2px 2px 3px #999;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
    }
    
    /* Rodapé e Regulamento */
    .regulamento-icon {
        display: block;
        text-align: center;
        margin-top: 20px;
        text-decoration: none;
        color: #555;
        font-size: 14px;
        font-weight: bold;
        transition: 0.3s;
        padding: 10px;
        border-radius: 5px;
    }
    .regulamento-icon:hover {
        background-color: #f0f0f0;
        color: #4CAF50;
    }
    .assinatura-footer {
        position: fixed;
        bottom: 15px;
        left: 20px;
        width: 130px;
        z-index: 9999;
        opacity: 0.8;
    }
    .sidebar-detalhe {
        font-size: 12px;
        color: #ddd;
        margin-bottom: 15px;
        line-height: 1.4;
    }
</style>

<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35">
</a>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
""", unsafe_allow_html=True)

# ------------------------------------------------------
# 5. MENU LATERAL
# ------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    
    # Navegação com botões
    if st.button("Home", use_container_width=True):
        st.session_state.pagina = "Home"
        st.session_state.pagamento_ativo = False
        st.rerun()
        
    if st.button("Preços", use_container_width=True):
        st.session_state.pagina = "Preços"
        st.session_state.pagamento_ativo = False
        st.rerun()

    if st.button("Cadastro", use_container_width=True):
        st.session_state.pagina = "Cadastro"
        st.session_state.pagamento_ativo = False
        st.rerun()

    if st.button("Dashboard", use_container_width=True):
        st
