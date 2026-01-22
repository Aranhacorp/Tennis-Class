import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. INICIALIZAÇÃO DO ESTADO (PREVINE ERROS DE ATRIBUTO)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 4. ESTILO CSS E ELEMENTOS VISUAIS (RESTAURA TUDO)
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
    .custom-card, .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .text-total { color: white !important; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL E ACADEMIAS RECOMENDADAS (RESTAURADOS)
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True):
        st.session_state.pagina = "Home"
        st.session_state.pagamento_ativo = False
        st.rerun()
    if st.button("Serviços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Produtos", use_container_width=True): st.session_state.pagina = "Produtos"
    if st.button("Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"
    
    st.markdown("<br><br>🏢 **Academias Recomendadas**", unsafe_allow_html=True)
    with st.expander("Play Tennis Ibirapuera"): st.write("Rua Joinville, 100")
    with st.expander("Top One tennis"): st.write("Av. Moema, 123")
    with st.expander("Fontes & Barbeta Tennis"): st.write("Rua Groenlândia, 456")
    with st.expander("Arena BTG"): st.write("Av. Faria Lima, 789")

# TÍTULO PRINCIPAL (RESTAURADO)
st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DE NAVEGAÇÃO E GRAVAÇÃO NA PLANILHA
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            opcoes = {
                "Aula Individual (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940,
                "Pacote 8 Aulas (R$ 1800)": 1800,
                "Aula Kids (R$ 230)": 230
            }
            pacote_sel = st.selectbox("Selecione o Pacote", list(opcoes.keys()))
            data_input = st.date_input("Escolha a Data")
            horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    # Mapeia exatamente para as colunas da sua TennisClass_DB
                    st.session_state.reserva_temp = {
                        "Data": data_input.strftime("%d/%m/%Y"),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Servico": "Aula",
                        "Pacote": pacote_sel,
                        "Status": "Aguardando Pagamento",
                        "Academia": ""
                    }
                    st.session_state.total_valor = opcoes[pacote_sel]
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO E GRAVAÇÃO
        st.markdown(f"<div class='text-total'>Total do Pacote: R$ {st.session_state.total_valor:.2f}</div>", unsafe_allow_html=True)
        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
        st.markdown("### Pagamento via PIX")
        st.code("aranha.corp@gmail.com.br", language=None)
        
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar", use_container_width=True):
                st.session_state.pagamento_ativo = False
                st.rerun()
        with col2:
            if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
                try:
                    # Lê dados atuais e concatena com o novo
                    df_atual = conn.read(worksheet="Página1")
                    novo_registro = pd.DataFrame([st.session_state.reserva_temp])
                    df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                    
                    # Atualiza a
