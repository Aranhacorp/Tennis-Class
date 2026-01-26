import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. INICIALIZAÇÃO DO ESTADO (PREVINE ERROS E SUMIÇOS)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 4. DESIGN E ESTILO (CSS) - RESTAURAÇÃO TOTAL
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
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .total-pagamento {
        color: white !important; font-size: 36px; font-weight: bold;
        margin: 25px 0; text-shadow: 3px 3px 5px rgba(0,0,0,0.5);
        text-align: center;
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
    academias = {
        "Play Tennis Ibirapuera": "Rua Estado de Israel, 860",
        "Top One tennis": "Avenida Indianapolis, 647",
        "Fontes & Barbeta Tennis": "Rua Oscar Gomes Cardim, 535",
        "Arena BTG": "Rua Major Sylvio de Magalhães Padilha, 16741"
    }
    for nome, end in academias.items():
        with st.expander(nome):
            st.write(f"📍 {end}")

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            pacotes = {
                "Aula Individual (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940,
                "Pacote 8 Aulas (R$ 1800)": 1800
            }
            pacote_sel = st.selectbox("Selecione o Pacote", list(pacotes.keys()))
            data_sel = st.date_input("Escolha a Data")
            hora_sel = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_sel.strftime("%Y-%m-%d"),
                        "Horario": hora_sel,
                        "Aluno": aluno,
                        "Servico": "Aula",
                        "Pacote": pacote_sel,
                        "Status": "Pendente",
                        "Academia": ""
                    }
                    st.session_state.total_valor = pacotes[pacote_sel]
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO - APENAS CHAVE PIX
        st.markdown(f"<div class='total-pagamento'>Total: R$ {st.session_state.total_valor:.2f}</div>", unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 💳 Pagamento via PIX")
        st.write("Copie a chave abaixo:")
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
                    df_atual = conn.read(worksheet="Página1")
                    nova_linha = pd.DataFrame([st.session_state.reserva_temp])
                    # Alinhamento exato com as colunas da TennisClass_DB
                    colunas = ["Data", "Horario", "Aluno", "Servico", "Pacote", "Status", "Academia
