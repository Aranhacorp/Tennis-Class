import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: DESIGN PADRONIZADO E BARRA LATERAL REDUZIDA
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .header-title {
        color: white;
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 20px !important;
        border-radius: 20px !important;
        min-width: 225px !important; 
        max-width: 225px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

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

    .whatsapp-float {
        position: fixed; width: 60px; height: 60px; bottom: 30px; right: 30px;
        background-color: #25d366; color: white !important; border-radius: 50px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; z-index: 1000; text-decoration: none !important;
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
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}"):
            st.session_state.menu_selecionado = item
            st.rerun()

# 4. TÍTULO NO TOPO
st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 5. CONTEÚDO
menu = st.session_state.menu_selecionado

if menu == "Home":
    st.markdown("<h2 style='text-align: center; color: white;'>Agendamento Profissional</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                servico = st.selectbox("Serviço", ["Aula Individual (R$ 250/hora)", "Aula em Dupla (R$ 200/pessoa)", "Aluguel de Quadra (R$ 250/hora)"])
                data = st.date_input("Data", format="DD/MM/YYYY")
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
                
                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        # Processamento da Planilha
                        data_br = data.strftime("%d/%m/%Y")
                        nova_linha = pd.DataFrame([{"Data": data_br, "Horario": horario, "Aluno": aluno, "Servico": servico, "Academia": academia}])
                        df_final = pd.concat([conn.read(), nova_linha], ignore_index=True)
                        conn.update(data=df_final)
                        
                        # AÇÃO DE SUCESSO
                        st.balloons() # Balões ativados
                        st.session_state.confirmado = True
                        st.rerun()

            # MENSAGEM ALTERADA PARA "Reserva realizada com sucesso!"
            if st.session_state.get('confirmado'):
                st.success("Reserva realizada com sucesso!") # Ajuste solicitado
