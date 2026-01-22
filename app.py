import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTILO CSS PADRONIZADO
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
    </style>
""", unsafe_allow_html=True)

# 4. CONTROLE DE NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True): 
        st.session_state.pagina = "Home"; st.rerun()
    if st.button("Cadastro", use_container_width=True): 
        st.session_state.pagina = "Cadastro"; st.rerun()

# --- LÓGICA DA PÁGINA HOME ---
if st.session_state.pagina == "Home":
    if 'pagamento_ativo' not in st.session_state:
        st.session_state.pagamento_ativo = False

    if not st.session_state.pagamento_ativo:
        # TELA DE AGENDAMENTO
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("reserva_form"):
            aluno = st.text_input("Nome do Aluno")
            pacote = st.selectbox("Pacotes", ["Aula Individual (R$ 250)", "Aula em Grupo (R$ 200)", "Aula Kids Pacote 4 Aulas (R$ 230/hora)"])
            data_reserva = st.date_input("Data")
            horario = st.selectbox("Horário", ["11:00", "12:00", "13:00", "14:00", "15:00"])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                st.session_state.reserva = {
                    "Data": data_reserva.strftime("%Y-%m-%d"),
                    "Horario": horario,
                    "Aluno": aluno,
                    "Pacote": pacote,
                    "Status": "Aguardando Pagamento"
                }
                st.session_state.pagamento_ativo = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # TELA DE PAGAMENTO E GRAVAÇÃO
        st.markdown(f"<h2 style='text-align: center; color: white;'>Total: {st.session_state.reserva['Pacote']}</h2>", unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        chave_pix = "aranha.corp@gmail.com.br"
        st.markdown(f"**Chave PIX (E-mail):**")
        st.code(chave_pix, language=None)
        
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
            # --- GRAVAÇÃO NA PLANILHA ---
            try:
                # Carrega dados atuais
                df_existente = conn.read(worksheet="Página1")
                # Cria novo registro
                novo_dado = pd.DataFrame([st.session_state.reserva])
                # Concatena e atualiza
                df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
                conn.update(worksheet="Página1", data=df_atualizado)
                
                st.balloons()
                st.success("Reserva gravada com sucesso na planilha!")
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao atualizar planilha: {e}")
        
        if st.button("Voltar"):
            st.session_state.pagamento_ativo = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    st.markdown(f'<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true" width="100%" height="800" frameborder="0" style="background:white; border-radius:15px;"></iframe>', unsafe_allow_html=True)
