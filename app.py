import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Tennis Class", layout="centered")

# 2. CSS para aplicar sua imagem de fundo (Universe 2025)
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://raw.githubusercontent.com/adrianosantospaiva/tennis-class/main/Universe%202025%20ahead.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Deixa as camadas frontais transparentes */
[data-testid="stMain"], [data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}

/* Estiliza o formulário para facilitar a leitura */
.stForm {
    background-color: rgba(255, 255, 255, 0.9);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.5);
}

/* Título em Branco para contrastar com o espaço */
.stMarkdown h1 {
    color: white !important;
    text-align: center;
    text-shadow: 2px 2px 8px #000000;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. Conteúdo do App
st.title("TENNIS CLASS 🎾")

conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("reserva_form"):
    st.write("### Agende sua Aula")
    aluno = st.text_input("Nome do Aluno")
    servico = st.selectbox("Serviço", ["Aula Individual", "Aula em Grupo", "Aluguel de Quadra"])
    data = st.date_input("Data")
    horario = st.time_input("Horário")
    
    submit = st.form_submit_button("RESERVAR AGORA")
    
    if submit:
        if not aluno:
            st.warning("Por favor, digite o nome.")
        else:
            nova_reserva = pd.DataFrame([{
                "Aluno": aluno, 
                "Servico": servico, 
                "Data": str(data), 
                "Horario": str(horario)
            }])
            dados = conn.read()
            df_atualizado = pd.concat([dados, nova_reserva], ignore_index=True)
            conn.update(data=df_atualizado)
            st.success("Reserva confirmada no universo do Tênis!")
            st.balloons()
