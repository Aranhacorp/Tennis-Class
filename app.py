import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 4. DESIGN E ESTILO (CSS CORRIGIDO)
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
    .valor-compra {
        font-size: 32px; color: #2E7D32; font-weight: bold; 
        background: #e8f5e9; padding: 20px; border-radius: 15px;
        margin: 20px 0; border: 2px solid #2E7D32;
    }
    .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 45px; border-radius: 30px;
        max-width: 650px; margin: 40px auto; text-align: center;
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .assinatura-aranha { position: fixed; bottom:
