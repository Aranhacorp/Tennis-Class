import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: DESIGN PADRONIZADO E BARRA LATERAL REDUZIDA
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* SIDEBAR REDUZIDA EM 20% (Aprox. 225px) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 20px !important;
        border-radius: 20px !important;
        min-width: 225px !important; 
        max-width: 225px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* CARD TRANSPARENTE PADRÃO (Utilizado na Home e no Contato) */
    .custom-card {
        background-color: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        color: white !important;
        max-width: 800px;
        margin: auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }

    /* Forçar cor branca em textos dentro dos cards */
    .custom-card h1, .custom-card h2, .custom-card h3, .custom-card p, .custom-card span {
        color: white !important;
    }

    /* Estilo dos Botões do Menu */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 50px !important;
        width: 100% !important;
    }

    /* Botão Flutuante WhatsApp */
    .whatsapp-float {
        position: fixed;
        width: 60px; height: 60px;
        bottom: 30px; right: 30px;
        background-color: #25d366;
        color: white !important;
        border-radius: 50px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; z-index: 1000;
        text-decoration: none !important;
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank"><i class="fa fa-whatsapp"></i></a>
""", unsafe_allow_html=True)

# 3. LÓGICA DE NAVEGAÇÃO
if 'menu_selecionado' not in st.session_state:
    st.session_state.menu_selecionado = "Home"

with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: white;'>🎾 TENNIS CLASS</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}"):
            st.session_state.menu_selecionado = item
            st.rerun()
        st.markdown(f"<div style='margin-top:-45px; text-align:right; color:rgba(255,255,255,0.4);'>▶</div><br>", unsafe_allow_html=True)

# 4. CONTEÚDO DINÂMICO
menu = st.session_state.menu_selecionado

if menu == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Agendamento Profissional</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                servico = st.selectbox("Selecione o Serviço", ["Aula Individual (R$ 250/hora)", "Aula em Dupla (R$ 200/pessoa)", "Aluguel de Quadra (R$ 250/hora)"])
                data = st.date_input("Data Desejada", format="DD/MM/YYYY")
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])
                # HORÁRIOS: 11:00 às 21:00
                horario = st.selectbox("Horário Disponível", [f"{h:02d}:00" for h in range(11, 22)])
                
                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        data_br = data.strftime("%d/%m/%Y")
                        nova_linha = pd.DataFrame([{"Data": data_br, "Horario": horario, "Aluno": aluno, "Servico": servico, "Academia": academia}])
                        df_final = pd.concat([conn.read(), nova_linha], ignore_index=True)
                        conn.update(data=df_final)
                        
                        # ATIVAÇÃO DOS BALÕES NA CONFIRMAÇÃO
                        st.balloons()
                        
                        st.session_state.confirmado = True
                        st.rerun()

            if st.session_state.get('confirmado'):
                st.success("Reserva realizada com sucesso!")
                qr = segno.make("25019727830")
                img_buffer = BytesIO()
                qr.save(img_buffer, kind='png', scale=5)
                st.image(img_buffer.getvalue(), width=200)
                st.code("250.197.278-30")
        except Exception:
            st.warning("Aguardando conexão com a planilha de agendamentos.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Cadastro":
    st.markdown("<h1 style='text-align: center; color: white;'>Cadastro de Professor</h1>", unsafe_allow_html=True)
    # Iframe do Google Forms
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfN-d-T_G2V_u_yN0_S_b8O_G2H_u_yN0_S_b8O_G2H_u_yN0_S_b/viewform?embedded=true"
    st.markdown(f'<div style="background:white; border-radius:15px; padding:10px;"><iframe src="{form_url}" width="100%" height="700" frameborder="0"></iframe></div>', unsafe_allow_html=True)

elif menu == "Contato":
    st.markdown("<h1 style='text-align: center; color: white;'>Fale Conosco</h1>", unsafe_allow_html=True)
    # CARD DE CONTATO COM TRANSPARÊNCIA E FONTE BRANCA
    st.markdown("""
        <div class="custom-card">
            <h1>André Aranha</h1>
            <hr style="border: 0.5px solid rgba(255,255,255,0.2); margin: 25px 0;">
            <p style="font-size: 22px;">📧 <strong>E-mail:</strong> aranha.corp@gmail.com.br</p>
            <p style="font-size: 22px;">📞 <strong>WhatsApp:</strong> 11 - 97142 5028</p>
            <br>
            <a href="https://wa.me/5511971425028" target="_blank" 
               style="background:#25d366; color:white; padding:15px 35px; border-radius:15px; text-decoration:none; font-weight:bold; display: inline-block;">
               INICIAR CONVERSA
            </a>
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"<h1 style='color: white; text-align: center;'>{menu}</h1>", unsafe_allow_html=True)
