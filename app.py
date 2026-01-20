import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. DESIGN, ASSINATURA E WHATSAPP FLUTUANTE
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
        background-color: rgba(0, 0, 0, 0.75) !important; backdrop-filter: blur(12px);
        padding: 40px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 850px; margin: auto; text-align: center; color: white !important;
    }
    
    /* Assinatura by Andre Aranha (Canto Inferior Esquerdo) */
    .assinatura-aranha {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 65px; /* Mesma proporção do WhatsApp */
        z-index: 1000;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
        transition: transform 0.3s;
    }
    .assinatura-aranha:hover { transform: scale(1.1); }

    /* WhatsApp Flutuante (Canto Inferior Direito) */
    .whatsapp-float {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        z-index: 1000;
        transition: transform 0.3s;
    }
    .whatsapp-float:hover { transform: scale(1.1); }
    </style>
    
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/by%20Andre%20Aranha.png" class="assinatura-aranha">
    
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 3. SISTEMA DE NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 4. LÓGICA DE PÁGINAS
menu = st.session_state.pagina

# --- PÁGINA HOME: AGENDAMENTO ---
if menu == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()

            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                precos = {
                    "Aula Individual (R$ 250/h)": 250,
                    "Aula em Dupla (R$ 200/pessoa)": 200,
                    "Aluguel de Quadra (R$ 250/h)": 250
                }
                servico = st.selectbox("Serviço", list(precos.keys()))
                n_horas = st.number_input("Horas", min_value=1, max_value=5, value=1)
                data = st.date_input("Data", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                academia
