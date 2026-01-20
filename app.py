import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: DESIGN DA SIDEBAR E ELEMENTOS VISUAIS
st.markdown("""
    <style>
    /* Fundo do App */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* SIDEBAR REFORMULADA (Largura de 280px para evitar textos encavalados) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 40px !important;
        border-radius: 20px !important;
        min-width: 280px !important; 
        max-width: 320px !important;
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Estilo dos Botões de Navegação com Seta */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 55px !important;
        text-align: left !important;
        padding-left: 20px !important;
        font-size: 17px !important;
        transition: 0.3s !important;
        width: 100% !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .stButton > button:hover {
        background-color: rgba(0, 212, 255, 0.2) !important;
        border-color: #00d4ff !important;
        transform: translateX(5px);
    }

    /* Card de Conteúdo Principal */
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 35px;
        border-radius: 20px;
        color: black;
        max-width: 850px;
        margin: auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Botão Flutuante WhatsApp */
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
        text-decoration: none !important;
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
        <i class="fa fa-whatsapp"></i>
    </a>
""", unsafe_allow_html=True)

# 3. LÓGICA DE NAVEGAÇÃO DA BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white; font-family: Arial Black;'>🎾 TENNIS CLASS</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'menu_selecionado' not in st.session_state:
        st.session_state.menu_selecionado = "Home"

    # Criando os itens do menu com setas indicadoras à direita
    def criar_item_menu(label):
        if st.button(label, key=f"btn_{label}"):
            st.session_state.menu_selecionado = label
            st.rerun()
        # Sobreposição visual da seta para garantir alinhamento perfeito
        st.markdown(f"<div style='margin-top:-48px; text-align:right; padding-right:20px; pointer-events:none; color:rgba(255,255,255,0.6);'>▶</div><br>", unsafe_allow_html=True)

    criar_item_menu("Home")
    criar_item_menu("Serviços")
    criar_item_menu("Produtos")
    criar_item_menu("Cadastro")
    criar_item_menu("Contato")

# 4. CONTEÚDO DINÂMICO
menu = st.session_state.menu_selecionado

if menu == "Home":
    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 4px #000;'>TENNIS CLASS</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📝 Agende sua Aula")
        
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                servico = st.selectbox("Serviço", ["Aula Individual", "Aula em Dupla", "Aluguel de Quadra"])
                data = st.date_input("Data Desejada", format="DD/MM/YYYY")
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])
                horario = st.selectbox("Horário", ["08:00", "10:00", "14:00", "16:00", "18:00"])
                
                if st.form_submit_button("GERAR RESERVA"):
                    if aluno:
                        data_br = data.strftime("%d/%m/%Y")
                        nova_linha = pd.DataFrame([{"Data": data_br, "Horario": horario, "Aluno": aluno, "Servico": servico, "Academia": academia}])
                        df_existente = conn.read()
                        df_final = pd.concat([df_existente, nova_linha], ignore_index=True)
                        conn.update(data=df_final)
                        st.session_state.confirmado = True
                        st.rerun()

            if st.session_state.get('confirmado'):
                st.success("Reserva realizada! Realize o pagamento abaixo:")
                qr = segno.make("25019727830")
                img_buffer = BytesIO()
                qr.save(img_buffer, kind='png', scale=5)
                st.image(img_buffer.getvalue(), width=200)
                st.code("250.197.278-30") # Correção do erro de aspas da imagem ae91c3
        except:
            st.error("Configure sua conexão GSheets para agendar.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Cadastro":
    st.markdown("<h1 style='text-align: center; color: white;'>Cadastro de Professor</h1>", unsafe_allow_html=True)
    # Iframe do Google Forms solicitado
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfN-d-T_G2V_u_yN0_S_b8O_G2H_u_yN0_S_b8O_G2H_u_yN0_S_b/viewform?embedded=true"
    st.markdown(f'<div style="background:white; border-radius:15px; padding:10px;"><iframe src="{form_url}" width="100%" height="800" frameborder="0"></iframe></div>', unsafe_allow_html=True)

elif menu == "Contato":
    st.markdown("<h1 style='text-align: center; color: white;'>Fale Conosco</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class="main-card" style="text-align: center;">
            <h2 style="color: #1e3d59;">André Aranha</h2>
            <p style="font-size: 18px;">📧 <strong>E-mail:</strong> aranha.corp@gmail.com.br</p>
            <p style="font-size: 18px;">📞 <strong>WhatsApp:</strong> 11 - 97142 5028</p>
            <br>
            <a href="https://wa.me/5511971425028" style="background:#25d366; color:white; padding:10px 20px; border-radius:10px; text-decoration:none;">Iniciar Conversa</a>
        </div>
    """, unsafe_allow_html=True)

else:
    st.info(f"A seção de {menu} está em desenvolvimento.")
