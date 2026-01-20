import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: DESIGN UNIFICADO (TRANSPARÊNCIA E FONTES BRANCAS)
st.markdown("""
    <style>
    /* Fundo do App */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* SIDEBAR REDUZIDA (225px) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 20px !important;
        border-radius: 20px !important;
        min-width: 225px !important; 
        max-width: 225px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* CARD DE CONTATO E CONTEÚDO (Transparência e Fonte Branca) */
    .custom-card {
        background-color: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        color: white !important;
        max-width: 700px;
        margin: auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }

    /* Ajuste de títulos e textos dentro do card */
    .custom-card h2, .custom-card p, .custom-card h1 {
        color: white !important;
        font-family: 'sans-serif';
    }

    /* Botões de Menu na Sidebar */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 50px !important;
        transition: 0.3s !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background-color: rgba(0, 212, 255, 0.2) !important;
        border-color: #00d4ff !important;
    }

    /* Botão Flutuante WhatsApp */
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
        z-index: 10
