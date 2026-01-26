import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. INICIALIZAÇÃO DO ESTADO (PREVINE ERROS DE ATRIBUTO E SUMIÇO DE ELEMENTOS)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 4. DESIGN E ESTILO (CSS)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 55px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }
    .custom-card {
        background-color: rgba(255, 255, 255, 0.98) !important; 
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 45px; border-radius: 30px;
        max-width: 650px; margin: 40px auto; text-align: center;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .total-pagamento {
        color: white !important; font-size: 36px; font-weight: bold;
        margin: 25px 0; text-shadow: 3px 3px 5px rgba(0,0,0,0.5);
        text-align: center;
    }
    .pix-info {
        background-color: #f0f2f6;
        border: 2px dashed #007bff;
        padding: 20px; border-radius: 15px; margin: 20px 0; color: #1E1E1E;
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 5. NAVEGAÇÃO LATERAL
with st
