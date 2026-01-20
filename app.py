import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="TENNIS CLASS", layout="centered")

# 2. CSS: Estilização do Fundo e Componentes
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 5px;
        width: 100%;
    }
    .header-container h1 {
        color: white !important;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px #000000;
        margin: 0;
    }
    /* Barra Branca Única com Texto Centralizado */
    .highlight-bar {
        background-color: white;
        height: 80px;
        width: 100%;
        border-radius: 15px;
        margin: 15px 0 25px 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .highlight-text {
        color: #1e3d59;
        font-weight: bold;
        font-size: 1.5rem;
        text-align: center;
    }
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    /* Ícone do WhatsApp */
    .whatsapp-float {
        position: fixed;
        width: 60px;
        height: 60px;
        bottom: 75px; 
        right: 20px;
        background-color: rgba(0, 0, 0, 0.6);
        color: white !important;
        border: 2px solid white;
        border-radius: 50px;
        text-align: center;
        font-size: 35px;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
    }
    </style>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
        <i class="fa fa-whatsapp"></i>
    </a>
    """, unsafe_allow_html=True)

# 3. Cabeçalho Principal
st.markdown("""
    <div class="header-container">
        <h1>TENNIS CLASS</h1>
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
    except Exception:
        st.error("Erro na conexão com a planilha.")

    with st.form("agendamento"):
        aluno = st.text_input("Nome do Aluno")
        
        servicos_lista = [
            "Aula Individual (R$ 250/hora)",
            "Aula em Dupla (R$ 200/hora cada)",
            "Aula com 3 Alunos (R$ 180/hora cada)",
            "Aula com 4 Alunos (R$ 150/hora cada)",
            "Aluguel de Quadra (R$ 250/hora)"
        ]
        servico = st.selectbox("Selecione o Serviço", servicos_lista)
        
        data = st.date_input("Data Desejada", format="DD/MM/YYYY")
        
        # --- LISTA DE ACADEMIAS FORMATADA ---
        academias_lista = [
            "Play Tennis Ibirapuera | R. Estado de Israel, 860",
            "Fontes e Barbeta Tenis | Rua Oscar Gomes Cardim, 535",
            "TOP One Tennis | Av. Indianópolis, 647",
            "Arena BTG Pactual Morumbi | Av. Major Sylvio de M. Padilha, 16741"
        ]
        academia = st.selectbox("Academia", academias_lista)
        
        horarios_aula = [
            "11:00 am", "12:00 pm", "13:00 pm", "14:00 pm", "15:00 pm", 
            "16:00 pm", "17:00 pm", "18:00 pm", "19:00 pm", "20:00 pm", "21:00 pm"
        ]
        horario = st.selectbox("Horário Disponível", horarios_aula)
        
        submit = st.form_submit_button("CONFIRMAR E GERAR QR CODE")
        
        if submit:
            if aluno:
                try:
                    data_br = data.strftime("%d/%m/%Y")
                    nova_linha = pd.DataFrame([{
                        "Data": data_br, 
                        "Horario": horario, 
                        "Aluno": aluno, 
                        "Servico": servico, 
                        "Academia": academia,
                        "Status": "Aguardando Pagamento"
                    }])
                    dados_existentes = conn.read()
                    df_final = pd.concat([dados_existentes, nova_linha], ignore_index=True)
                    conn.update(data=df_final)
                    
                    st.balloons() 
                    st.session_state['confirmado'] = True
                    st.session_state['serv_v'] = servico
                    st.success(f"Reserva realizada para {aluno} na {academia.split('|')[0].strip()}!")
                except Exception as e:
                    st.error(f"Erro ao salvar dados: {e}")
            else:
                st.warning("Por favor, preencha o nome do aluno.")

    if st.session_state.get('confirmado'):
        st.markdown("---")
        st.markdown('<div style="text-align: center; color: black;">', unsafe_allow_html=True)
        st.markdown("### 💰 Pagamento via PIX")
        st.write(f"**Serviço:** {st.session_state['serv_v']}")
        
        qr = segno.make("25019727830")
        img_buffer = BytesIO()
        qr.save(img_buffer, kind='png', scale=7)
        st.image(img_buffer.getvalue(), width=250)
        
        st.code("250.197.278-30", language="text")
        st.write("Após o pagamento, envie o comprovante para: (11) 97142-5028")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
