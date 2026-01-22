import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTILO CSS PADRONIZADO (CINZA TRANSPARENTE)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .custom-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-pagamento {
        color: white !important; font-size: 32px; font-weight: bold; 
        text-align: center; margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. NAVEGAÇÃO LATERAL
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True): 
        st.session_state.pagina = "Home"; st.rerun()
    if st.button("Cadastro", use_container_width=True): 
        st.session_state.pagina = "Cadastro"; st.rerun()

# --- PÁGINA HOME ---
if st.session_state.pagina == "Home":
    if 'pagamento_ativo' not in st.session_state:
        st.session_state.pagamento_ativo = False

    if not st.session_state.pagamento_ativo:
        # TELA DE AGENDAMENTO
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("reserva_form"):
            aluno = st.text_input("Nome do Aluno")
            pacote = st.selectbox("Pacotes", [
                "Aula Individual Pacote 4 Aulas (R$ 235/hora)",
                "Aula Individual Pacote 8 Aulas (R$ 225/hora)",
                "Aula Kids Pacote 4 Aulas (R$ 230/hora)"
            ])
            data_reserva = st.date_input("Data")
            horario = st.selectbox("Horário", ["11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva = {
                        "Data": data_reserva.strftime("%d/%m/%Y"),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Pacote": pacote,
                        "Status": "Pendente"
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else:
                    st.error("Por favor, insira o nome do aluno.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # TELA DE PAGAMENTO (QR CODE REMOVIDO)
        st.markdown(f"<div class='total-pagamento'>Total do Pacote: {st.session_state.reserva['Pacote'].split('(')[-1].replace(')', '')}</div>", unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        st.markdown("### Realize o PIX para confirmar")
        
        # Chave PIX e Cópia (Sem Favorecido)
        chave_pix = "aranha.corp@
