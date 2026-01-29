import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando)
st.set_page_config(page_title="TENNIS CLASS", layout="wide", page_icon="🎾")

# 2. CONEXÃO COM GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO (Memória do App)
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'inicio_timer' not in st.session_state: st.session_state.inicio_timer = None
if 'admin_autenticado' not in st.session_state: st.session_state.admin_autenticado = False

# 4. CSS GLOBAL E COMPONENTES VISUAIS
# Uso de aspas triplas para evitar SyntaxError em blocos grandes
st.markdown("""
<style>
    /* Fundo com imagem e sobreposição escura */
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
    
    /* Cartões Translúcidos */
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
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
    
    /* Botões de Cadastro Clean (Sem fundo verde pesado) */
    .btn-cadastro-clean {
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
        color: white !important; 
        text-decoration: none; 
        font-weight: bold; 
        text-align: center;
        transition: 0.3s; 
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.1); /* Leve fundo para clique */
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .btn-cadastro-clean:hover { 
        transform: scale(1.05); 
        background-color: rgba(76, 175, 80, 0.8); /* Verde ao passar o mouse */
        border-color: #4CAF50;
    }
    .icon-large { font-size: 60px; margin-bottom: 10px; }
    
    /* WhatsApp Flutuante Fixo */
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
        z-index: 9999; /* Garante que fique acima de tudo */
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-decoration: none;
    }
    .whatsapp-float:hover { color: white; transform: scale(1.1); transition: 0.3s; }

    /* Assinatura */
    .assinatura-footer { 
        position: fixed; 
        bottom: 10px; 
        left: 20px; 
        width: 120px; 
        opacity: 0.7; 
        z-index: 9999; 
    }
    .sidebar-detalhe { font-size: 12px; color: #ccc; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Elementos Flutuantes (Injetados fora do fluxo principal)
st.markdown("""
<a href="https://wa.me/5511971425028" class="whatsapp-float
