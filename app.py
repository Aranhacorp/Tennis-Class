import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="TENNIS CLASS", layout="centered")

# 2. CSS: Sidebar Sensível (Fim do erro de duplo clique), Transparência e Quadrados
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
    
    /* SIDEBAR FLUTUANTE (180px) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.75) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 60px !important;
        border-radius: 25px !important;
        min-width: 180px !important;
        max-width: 180px !important;
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
        z-index: 9999;
    }

    /* AJUSTE PARA CLIQUE ÚNICO E SENSIBILIDADE */
    /* Garante que o clique passe através de camadas fantasmas */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        cursor: pointer !important;
        padding: 8px 10px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        transition: background 0.3s ease;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    /* QUADRADOS DE SELEÇÃO */
    div[data-testid="stRadio"] div[role="radiogroup"] label div:first-child {
        border-radius: 4px !important;
        width: 18px !important;
        height: 18px !important;
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        margin-right: 10px !important;
    }
    
    /* Indicador de Seleção Ativa */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div:first-child div:first-child {
        background-color: #00b4d8 !important; /* Azul Neon para visibilidade */
        border-radius: 2px !important;
        width: 10px !important;
        height: 10px !important;
    }

    /* Estilo do Texto do Menu */
    [data-testid="stSidebar"] .stMarkdown p {
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px !important;
        margin: 0 !important;
    }

    /* Layout do Cartão Principal */
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        color: black;
    }

    .highlight-bar {
        background-color: white;
        height: 80px;
        width: 100%;
        border-radius: 15px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .whatsapp-float {
        position: fixed;
        width: 60px;
        height: 60px;
        bottom: 40px; 
        right: 20px;
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
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
        <i class="fa fa-whatsapp"></i>
    </a>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: white;'>🎾 TENNIS CLASS</h3>", unsafe_allow_html=True)
    st.write("")
    menu = st.radio(
        "Menu",
        ["Home", "Serviços", "Cadastros", "Produtos", "Contato"],
        label_visibility="collapsed"
    )
    st.write("---")

# 4. LÓGICA DE NAVEGAÇÃO
if menu == "Home":
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px;">
            <h1 style="color:white; font-family:'Arial Black'; text-shadow:2px 2px 4px #000;">TENNIS CLASS</h1>
            <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/tennis-player-silhouette%20ver2.jpg" width="70" style="border-radius:10px; mix-blend-mode:screen;">
        </div>
        <div class="highlight-bar">
            <h2 style="color:#1e3d59; font-weight:bold; margin:0;">Agendamento Profissional</h2>
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
            aluno = st.text_input("Nome do Aluno")
            servico = st.selectbox("Serviço", ["Aula Individual", "Aula em Dupla", "Aluguel de Quadra"])
            data = st.date_input("Data Desejada", format="DD/MM/YYYY")
            
            academias = [
                "Play Tennis Ibirapuera | R. Estado de Israel, 860",
                "Fontes e Barbeta Tenis | Rua Oscar Gomes Cardim, 535",
                "TOP One Tennis | Av. Indianópolis, 647",
                "Arena BTG Pactual Morumbi | Av. Major Sylvio de M. Padilha, 16741"
            ]
            academia = st.selectbox("Academias recomendadas", academias)
            horario = st.selectbox("Horário", ["11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            
            submit = st.form_submit_button("CONFIRMAR E GERAR QR CODE")
            
            if submit and aluno:
                try:
                    data_br = data.strftime("%d/%m/%Y")
                    nova_linha = pd.DataFrame([{"Data": data_br, "Horario": horario, "Aluno": aluno, "Servico": servico, "Academia": academia}])
                    dados_existentes = conn.read()
                    df_final = pd.concat([dados_existentes, nova_linha], ignore_index=True)
                    conn.update(data=df_final)
                    st.balloons()
                    st.session_state['confirmado'] = True
                except Exception as e:
                    st.error(f"Erro: {e}")

        if st.session_state.get('confirmado'):
            st.markdown("---")
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            st.markdown("### 💰 Pagamento via PIX")
            qr = segno.make("25019727830")
            img_buffer = BytesIO()
            qr.save(img_buffer, kind='png', scale=7)
            st.image(img_buffer.getvalue(), width=250)
            st.code("250.197.278-30", language="text")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='color:white; text-align:center; margin-top:50px;'>{menu}</h1>", unsafe_allow_html=True)
