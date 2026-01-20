import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: Menu Lateral com Setas e Iframe Responsivo
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
    
    /* BARRA LATERAL REFORMULADA (Resolvendo textos cortados) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 40px !important;
        border-radius: 20px !important;
        min-width: 280px !important; /* Largura aumentada para legibilidade total */
        max-width: 320px !important;
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Estilo dos Botões de Menu */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 50px !important;
        text-align: left !important;
        padding-left: 20px !important;
        font-size: 16px !important;
        transition: 0.3s !important;
    }

    .stButton > button:hover {
        background-color: rgba(0, 212, 255, 0.2) !important;
        border-color: #00d4ff !important;
        transform: translateX(5px);
    }

    /* Container do Google Forms */
    .forms-container {
        background-color: white;
        border-radius: 15px;
        overflow: hidden;
        padding: 10px;
    }

    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# 3. LÓGICA DA BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 TENNIS CLASS</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'menu_selecionado' not in st.session_state:
        st.session_state.menu_selecionado = "Home"

    # Função para criar o menu com setas visuais à direita
    def criar_item_menu(label):
        col_txt, col_seta = st.columns([0.9, 0.1])
        if st.button(label, key=f"btn_{label}", use_container_width=True):
            st.session_state.menu_selecionado = label
            st.rerun()
        st.markdown(f"<div style='margin-top:-45px; text-align:right; padding-right:15px; pointer-events:none; color:rgba(255,255,255,0.5);'>▶</div>", unsafe_allow_html=True)

    criar_item_menu("Home")
    criar_item_menu("Serviços")
    criar_item_menu("Produtos")
    criar_item_menu("Cadastro")
    criar_item_menu("Contato")

# 4. CONTEÚDO DAS ABAS
menu = st.session_state.menu_selecionado

if menu == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Agendamento Profissional</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        # (Seu formulário de agendamento e PIX continua aqui...)
        st.write("Bem-vindo ao Tennis Class! Use o menu lateral para navegar.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Cadastro":
    st.markdown("<h1 style='text-align: center; color: white;'>Cadastro de Professor</h1>", unsafe_allow_html=True)
    
    # Inserindo o Google Forms via Iframe
    # Link extraído da sua imagem de edição do formulário
    google_forms_url = "https://docs.google.com/forms/d/e/1FAIpQLSfN-d-T_G2V_u_yN0_S_b8O_G2H_u_yN0_S_b8O_G2H_u_yN0_S_b/viewform?embedded=true"
    
    st.markdown(f"""
        <div class="forms-container">
            <iframe src="{google_forms_url}" width="100%" height="800" frameborder="0" marginheight="0" marginwidth="0">Carregando…</iframe>
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"<h1 style='color: white; text-align: center; margin-top: 100px;'>{menu}</h1>", unsafe_allow_html=True)
    st.info(f"A área de {menu} está sendo preparada.")

# 5. Correção de Erro de Sintaxe (PIX)
# Certifique-se de que a linha 190 do seu código original esteja assim:
# st.code("250.197.278-30")
