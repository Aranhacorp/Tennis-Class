import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: CARD BRANCO, ASSINATURA AMPLIADA E WHATSAPP ELEVADO
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
    
    /* Card BRANCO conforme solicitado */
    .custom-card {
        background-color: rgba(255, 255, 255, 0.95) !important; 
        backdrop-filter: blur(10px);
        padding: 40px; border-radius: 25px; 
        border: 1px solid rgba(0, 0, 0, 0.1);
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important;
    }
    
    .service-item {
        background: rgba(0, 0, 0, 0.05); padding: 15px; border-radius: 15px;
        margin: 10px 0; border: 1px solid rgba(0, 0, 0, 0.1);
        font-size: 1.2rem; color: #1E1E1E;
    }
    
    /* Assinatura ampliada (40% maior) */
    .assinatura-aranha {
        position: fixed; bottom: 25px; left: 25px;
        width: 180px; z-index: 9999;
        filter: drop-shadow(2px 2px 5px rgba(0,0,0,0.8));
    }
    
    /* WhatsApp elevado em 1cm */
    .whatsapp-float {
        position: fixed; bottom: 70px; right: 25px;
        width: 60px; z-index: 9999;
    }
    </style>
    
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

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
                st.markdown("<p style='color: #1E1E1E; font-weight: bold;'>Preencha os dados abaixo:</p>", unsafe_allow_html=True)
                aluno = st.text_input("Nome do Aluno")
                
                # NOME ALTERADO PARA 'PACOTES' CONFORME SOLICITADO
                pacote = st.selectbox("Pacotes", [
                    "Aula Particular", "Aula em Grupo", "Aula Kids", 
                    "Locação de Quadra", "Treinamento Esportivo", "Evento"
                ])
                
                n_horas = st.number_input("Horas", min_value=1, value=1)
                data = st.date_input("Data")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                
                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        # Correção de sintaxe para evitar Script Error
                        data_str = data.strftime("%Y-%m-%d")
                        nova_reserva = pd.DataFrame([{
                            "Data": data_str, 
                            "Horario": horario, 
                            "Aluno": aluno, 
                            "Servico": pacote, 
                            "Status": "Pendente"
                        }])
                        df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success("Reserva realizada com sucesso!")
        except Exception:
            st.info("Aguardando conexão com a planilha...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA SERVIÇOS ---
elif menu == "Serviços":
    st.markdown("<h2 style='text-align: center; color: white;'>Nossos Serviços</h2>", unsafe_allow_html=True)
