import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO E CONEXÃO
st.set_page_config(page_title="TENNIS CLASS", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. INICIALIZAÇÃO DE VARIÁVEIS (PREVINE ERRO DE ATRIBUTO)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 3. ESTILO CSS (CORREÇÃO DE ASPAS ABERTAS)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .custom-card, .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 30px; border-radius: 20px; text-align: center; color: white !important;
    }
    .total-valor { font-size: 32px; font-weight: bold; color: white; text-align: center; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# 4. NAVEGAÇÃO
with st.sidebar:
    if st.button("Home", use_container_width=True):
        st.session_state.pagina = "Home"
        st.session_state.pagamento_ativo = False
        st.rerun()
    if st.button("Cadastro", use_container_width=True):
        st.session_state.pagina = "Cadastro"
        st.rerun()

# --- FLUXO HOME E GRAVAÇÃO NA PLANILHA ---
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("agendamento"):
            aluno = st.text_input("Nome do Aluno")
            pacote = st.selectbox("Pacote", ["Aula Individual (R$ 250)", "Pacote 4 Aulas (R$ 940)", "Pacote 8 Aulas (R$ 1800)"])
            data = st.date_input("Data")
            hora = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
            
            if st.form_submit_button("AVANÇAR"):
                if aluno:
                    # Prepara os dados conforme as colunas da sua planilha TennisClass_DB
                    st.session_state.reserva_temp = {
                        "Data": data.strftime("%d/%m/%Y"),
                        "Horario": hora,
                        "Aluno": aluno,
                        "Servico": "Aula",
                        "Pacote": pacote,
                        "Status": "Pendente",
                        "Academia": "" # Campo vazio conforme sua planilha
                    }
                    st.session_state.total_valor = 250 if "250" in pacote else (940 if "940" in pacote else 1800)
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO (SEM QR CODE)
        st.markdown(f'<div class="total-valor">Total: R$ {st.session_state.total_valor:.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
        st.write("### Pagamento via PIX")
        st.code("aranha.corp@gmail.com.br", language=None)
        
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        if st.button("CONFIRMAR AGENDAMENTO E SALVAR", type="primary"):
            try:
                # LÓGICA DE ATUALIZAÇÃO DA PLANILHA
                df_atual = conn.read(worksheet="Página1")
                novo_registro = pd.DataFrame([st.session_state.reserva_temp])
                df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                
                # Atualiza a planilha TennisClass_DB
                conn.update(worksheet="Página1", data=df_final)
                
                st.balloons()
                st.success("Dados gravados com sucesso na planilha!")
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao acessar a planilha: {e}")
        
        if st.button("Voltar"):
            st.session_state.pagamento_ativo = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Cadastro</h2>", unsafe_allow_html=True)
    st.info("Selecione o perfil para abrir o formulário.")
