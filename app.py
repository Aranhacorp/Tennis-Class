import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="TENNIS CLASS", layout="centered")

# 2. CSS: Fundo, Sidebar FLUTUANTE e Layout
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
    
    /* SIDEBAR FLUTUANTE */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 60px; /* 60px de espaço da esquerda */
        border-radius: 20px; /* Bordas arredondadas */
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }
    
    /* Remove a borda padrão que o Streamlit coloca */
    [data-testid="stSidebarNav"] {
        background-color: transparent !important;
    }

    /* Texto da Sidebar em Branco */
    [data-testid="stSidebar"] * {
        color: white !important;
        font-family: 'Arial', sans-serif;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 5px;
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
    
    .highlight-text {
        color: #1e3d59;
        font-weight: bold;
        font-size: 1.5rem;
    }
    
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
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
    st.markdown("<h2 style='text-align: center;'>🎾 TENNIS CLASS</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio(
        "Navegação",
        ["Home", "Serviços", "Cadastros", "Produtos", "Contato"]
    )
    st.write("---")
    st.caption("Acompanhe suas aulas e agendamentos com facilidade.")

# 4. LÓGICA DE NAVEGAÇÃO
if menu == "Home":
    st.markdown("""
        <div class="header-container">
            <h1 style="color:white; font-family:'Arial Black'; text-shadow:2px 2px 4px #000;">TENNIS CLASS</h1>
            <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/tennis-player-silhouette%20ver2.jpg" width="70" style="border-radius:10px; mix-blend-mode:screen;">
        </div>
        <div class="highlight-bar">
            <span class="highlight-text">Agendamento Profissional</span>
        </div>
        """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📝 Agende sua Aula")
        
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
        except:
            st.error("Erro na conexão com a planilha.")

        with st.form("agendamento"):
            aluno = st.text_input("Nome do Aluno")
            servico = st.selectbox("Selecione o Serviço", [
                "Aula Individual (R$ 250/hora)", 
                "Aula em Dupla (R$ 200/pessoa)", 
                "Aluguel de Quadra (R$ 250/hora)"
            ])
            data = st.date_input("Data Desejada", format="DD/MM/YYYY")
            
            academias = [
                "Play Tennis Ibirapuera | R. Estado de Israel, 860",
                "Fontes e Barbeta Tenis | Rua Oscar Gomes Cardim, 535",
                "TOP One Tennis | Av. Indianópolis, 647",
                "Arena BTG Pactual Morumbi | Av. Major Sylvio de M. Padilha, 16741"
            ]
            academia = st.selectbox("Academias recomendadas", academias)
            horario = st.selectbox("Horário Disponível", ["11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            
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
                    st.error(f"Erro ao salvar: {e}")

        if st.session_state.get('confirmado'):
            st.markdown("---")
            st.markdown("<div style='text-align:center; color:black;'>", unsafe_allow_html=True)
            st.markdown("### 💰 Pagamento via PIX")
            qr = segno.make("25019727830")
            img_buffer = BytesIO()
            qr.save(img_buffer, kind='png', scale=7)
            st.image(img_buffer.getvalue(), width=250)
            st.code("250.197.278-30", language="text") # Linha corrigida
            st.write("Após o pagamento, envie o comprovante.")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
