import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: DESIGN UNIFICADO (BARRA LATERAL -20% E CARDS TRANSPARENTES)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* SIDEBAR REDUZIDA EM 20% (Aprox. 225px) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 20px !important;
        border-radius: 20px !important;
        min-width: 225px !important; 
        max-width: 225px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* CARD TRANSPARENTE PADRÃO (Utilizado na Home e no Contato) */
    .custom-card {
        background-color: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        color: white !important;
        max-width: 800px;
        margin: auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }

    /* Forçar cor branca em textos e títulos dentro dos cards */
    .custom-card h1, .custom-card h2, .custom-card h3, .custom-card p, .custom-card span {
        color: white !important;
    }

    /* Estilo dos Botões do Menu na Sidebar */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 50px !important;
        width: 100% !important;
    }

    /* Botão Flutuante WhatsApp */
    .whatsapp-float {
        position: fixed;
        width: 60px; height: 60px;
        bottom: 30px; right: 30px;
        background-color: #25d366;
        color: white !important;
        border-radius: 50px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; z-index: 1000;
        text-decoration: none !important;
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank"><i class="fa fa-whatsapp"></i></a>
""", unsafe_allow_html=True)

# 3. LÓGICA DE NAVEGAÇÃO
if 'menu_selecionado' not in st.session_state:
    st.session_state.menu_selecionado = "Home"

with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: white;'>🎾 TENNIS CLASS</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}"):
            st.session_state.menu_selecionado = item
            st.rerun()
        st.markdown(f"<div style='margin-top:-45px; text-align:right; color:rgba(255,255,255,0.4);'>▶</div><br>", unsafe_allow_html=True)

# 4. CONTEÚDO DINÂMICO
menu = st.session_state.menu_selecionado

if menu == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Agendamento Profissional</h1>",
