import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: Layout, Sidebar Flutuante e Design Responsivo
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* SIDEBAR FLUTUANTE REFORMULADA (280px para evitar textos cortados) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 40px !important;
        border-radius: 20px !important;
        min-width: 280px !important; 
        max-width: 320px !important;
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Botões de Menu Estilo Lista */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 55px !important;
        text-align: left !important;
        padding-left: 20px !important;
        font-size: 17px !important;
        transition: 0.3s !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background-color: rgba(0, 212, 255, 0.2) !important;
        border-color: #00d4ff !important;
        transform: translateX(5px);
    }

    /* Card Branco Principal */
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 35px;
        border-radius: 20px;
        color: black;
        max-width: 850px;
        margin: auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Barra de Destaque */
    .highlight-bar {
        background-color: white;
        height: 80px;
        width: 100%;
        max-width: 850px;
        border-radius: 15px;
        margin: 10px auto 25px auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Botão WhatsApp */
    .whatsapp-float {
        position: fixed;
        width: 60px;
        height: 60px;
        bottom: 30px; 
        right: 30px;
        background-color: #25d366;
        color: white !important;
        border-radius: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        z-index: 1000;
        text-decoration: none !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
        <i class="fa fa-whatsapp"></i>
    </a>
""", unsafe_allow_html=True)

# 3. LÓGICA DA BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white; font-family: Arial Black;'>🎾 TENNIS CLASS</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'menu_selecionado' not in st.session_state:
        st.session_state.menu_selecionado = "Home"

    def
