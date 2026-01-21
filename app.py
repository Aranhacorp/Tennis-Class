import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. ESTILO CSS PADRONIZADO (CINZA TRANSPARENTE + FONTE BRANCA)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    /* Estilo do balão cinza transparente */
    .custom-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .titulo-total {
        color: white !important; font-size: 32px; font-weight: bold; 
        text-align: center; margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO LATERAL
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True): st.session_state.pagina = "Home"; st.rerun()
    if st.button("Serviços", use_container_width=True): st.session_state.pagina = "Serviços"; st.rerun()
    if st.button("Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"; st.rerun()
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"; st.rerun()

# --- PÁGINA HOME: PAGAMENTO ---
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Finalizar Reserva</h1>", unsafe_allow_html=True)
    
    # Exemplo de valor
    st.markdown("<div class='titulo-total'>Total do Pacote: R$ 600,00</div>", unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # QR Code Corrigido (Caminho direto do GitHub)
    st.markdown("### Escaneie o QR Code para pagar")
    qr_url = "https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Andre%20Aranha%20Cagno%20-%20Chave%20PIX%20Banco%20Inter.png"
    st.image(qr_url, width=280)

    # Chave PIX e Funcionalidade de Cópia
    chave_pix = "aranha.corp@gmail.com.br"
    st.markdown(f"**Chave PIX (E-mail):**")
    st.code(chave_pix, language=None) # Ícone de cópia nativo e funcional
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.file_uploader("Anexe o comprovante aqui", type=['png', 'jpg', 'pdf'])
    
    if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
        st.
