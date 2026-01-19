import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="SPORTS CLASS", layout="centered")

# 2. CSS corrigido com o link da SUA imagem no repositório Tennis-Class
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    h1 {
        color: #003366;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1>SPORTS CLASS 🎾</h1>', unsafe_allow_html=True)

# Bloco de Agendamento
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Agende sua Aula")
    
    # Conexão com a planilha (usando o seu segredo configurado)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    with st.form("agendamento"):
        aluno = st.text_input("Nome do Aluno")
        servico = st.selectbox("Serviço", ["Aula Individual", "Aula em Dupla", "Aluguel de Quadra"])
        data = st.date_input("Data")
        horario = st.time_input("Horário")
        
        submit = st.form_submit_button("RESERVAR AGORA")
        
        if submit:
            if aluno:
                st.success(f"Solicitação enviada para {aluno}!")
                st.balloons()
            else:
                st.warning("Por favor, preencha seu nome.")
    st.markdown('</div>', unsafe_allow_html=True)
