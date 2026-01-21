import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. ESTILO CSS (PADRÃO CINZA TRANSPARENTE + FONTE BRANCA)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }
    /* Balão cinza com transparência e fonte branca */
    .custom-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: white !important; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-pagamento {
        color: white !important; font-size: 36px; font-weight: bold; 
        margin: 20px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .pix-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 10px; margin: 15px 0;
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 3. CONTROLE DE NAVEGAÇÃO (CORRIGIDO)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("🏠 Home", use_container_width=True): st.session_state.pagina = "Home"; st.rerun()
    if st.button("🎾 Serviços", use_container_width=True): st.session_state.pagina = "Serviços"; st.rerun()
    if st.button("📋 Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"; st.rerun()
    if st.button("📞 Contato", use_container_width=True): st.session_state.pagina = "Contato"; st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# --- PÁGINA HOME: AGENDAMENTO E PAGAMENTO ---
if st.session_state.pagina == "Home":
    if 'pagamento_ativo' not in st.session_state:
        st.session_state.pagamento_ativo = False

    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            opcoes_pacotes = {
                "Aula Individual Pacote 4 Aulas (R$ 235/h)": 940,
                "Aula Individual Pacote 8 Aulas (R$ 225/h)": 1800,
                "Aula Individual Única (R$ 250/h)": 250,
                "Aula Kids Pacote 4 Aulas (R$ 230/h)": 920,
                "Aula em Grupo até 3 pessoas (R$ 200/h)": 600,
                "Loc
