import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: Menu Lateral com Setas à Direita e Design Limpo
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
    
    /* BARRA LATERAL REFORMULADA */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 40px !important;
        border-radius: 20px !important;
        min-width: 260px !important; /* Largura ideal para não cortar texto */
        max-width: 300px !important;
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px !important;
    }

    /* ESTILO DOS BOTÕES DE MENU (SETAS À DIREITA) */
    .menu-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px 20px;
        margin: 8px 0;
        border-radius: 12px;
        color: white;
        text-decoration: none;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        transition: 0.3s;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .menu-item:hover {
        background-color: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
        color: #00d4ff !important;
    }

    .active-item {
        background-color: rgba(0, 212, 255, 0.2);
        border: 1px solid #00d4ff;
        color: #00d4ff !important;
    }

    /* Ícone de Seta */
    .arrow {
        font-size: 12px;
        opacity: 0.7;
    }

    /* Container Principal */
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        color: black;
    }

    .header-bar {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }

    .whatsapp-float {
        position: fixed;
        width: 60px;
        height: 60px;
        bottom: 30px; 
        right: 30px;
        background-color: #25d366;
        color: white !important;
        border-radius: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DA BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 TENNIS CLASS</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Inicializa o estado do menu se não existir
    if 'menu_selecionado' not in st.session_state:
        st.session_state.menu_selecionado = "Home"

    # Função para criar itens de menu clicáveis
    def criar_menu(label):
        estilo = "menu-item active-item" if st.session_state.menu_selecionado == label else "menu-item"
        if st.button(f"{label}", key=f"btn_{label}", use_container_width=True):
            st.session_state.menu_selecionado = label
            st.rerun()
        # Adiciona a seta visual via HTML logo abaixo do botão invisível do Streamlit para manter o design
        st.markdown(f"""
            <div style="margin-top: -45px; pointer-events: none; display: flex; justify-content: space-between; padding: 0 15px; margin-bottom: 20px;">
                <span style="color: transparent;">{label}</span>
                <span style="color: white; opacity: 0.5;">▶</span>
            </div>
        """, unsafe_allow_html=True)

    # Lista de Tópicos
    criar_menu("Home")
    criar_menu("Serviços")
    criar_menu("Produtos")
    criar_menu("Cadastro")
    criar_menu("Contato")

# 4. CONTEÚDO PRINCIPAL
menu = st.session_state.menu_selecionado

if menu == "Home":
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: white; font-size: 3rem; text-shadow: 2px 2px 5px black; margin-bottom: 10px;">TENNIS CLASS</h1>
        </div>
        <div class="header-bar">
            <h2 style="color: #1e3d59; margin: 0; font-weight: bold;">Agendamento Profissional</h2>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📝 Agende sua Aula")
        
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
        except:
            st.error("Erro na conexão.")

        with st.form("agendamento"):
            nome = st.text_input("Nome do Aluno")
            servico = st.selectbox("Selecione o Serviço", ["Aula Individual", "Aula em Dupla", "Aluguel de Quadra"])
            data = st.date_input("Data Desejada", format="DD/MM/YYYY")
            academia = st.selectbox("Academias recomendadas", [
                "Play Tennis Ibirapuera | R. Estado de Israel, 860",
                "Fontes e Barbeta Tenis | Rua Oscar Gomes Cardim, 535",
                "TOP One Tennis | Av. Indianópolis, 647",
                "Arena BTG Pactual Morumbi | Av. Major Sylvio de M. Padilha, 16741"
            ])
            submit = st.form_submit_button("CONFIRMAR AGENDAMENTO")
            
            if submit and nome:
                st.balloons()
                st.session_state.confirmado = True

        if st.session_state.get('confirmado'):
            st.markdown("---")
            st.markdown("<div style='text-align: center;'><h3>💰 Pagamento PIX</h3>", unsafe_allow_html=True)
            qr = segno.make("25019727830")
            img_buffer = BytesIO()
            qr.save(img_buffer, kind='png', scale=7)
            st.image(img_buffer.getvalue(), width=200)
            st.code("250.197.278-30")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"<h1 style='color: white; text-align: center; margin-top: 100px;'>{menu}</h1>", unsafe_allow_html=True)
    st.info(f"Página de {menu} em desenvolvimento.")

# Botão flutuante WhatsApp
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
        <i class="fa fa-whatsapp"></i>
    </a>
""", unsafe_allow_html=True)
