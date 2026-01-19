import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página (Título na aba do navegador)
st.set_page_config(page_title="Tennis Class - Agendamento", layout="centered")

# 2. Estilização CSS (Imagem de Fundo e Transparência)
page_bg_img = """
<style>
/* Imagem de fundo no container principal */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1595435064219-49293a10173d?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Deixa o fundo do Streamlit transparente para a imagem aparecer */
[data-testid="stMain"], [data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}

/* Estiliza a caixa do formulário */
.stForm {
    background-color: rgba(255, 255, 255, 0.95) !important;
    padding: 30px !important;
    border-radius: 15px !important;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}

/* Estilo para o Título principal */
.titulo-principal {
    color: white;
    text-shadow: 2px 2px 4px #000000;
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. Conteúdo da Tela
st.markdown('<p class="titulo-principal">TENNIS CLASS 🎾</p>', unsafe_allow_html=True)

# Conexão com a planilha (usando os Secrets que já configuramos)
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("agendamento"):
    st.subheader("Faça sua reserva")
    
    aluno = st.text_input("Nome do Aluno")
    data = st.date_input("Escolha a Data")
    horario = st.time_input("Escolha o Horário")
    
    submit = st.form_submit_button("RESERVAR AGORA")

    if submit:
        if aluno == "":
            st.error("Por favor, preencha o nome do aluno.")
        else:
            # Lógica para salvar na planilha
            nova_linha = pd.DataFrame([{"Aluno": aluno, "Data": str(data), "Horario": str(horario)}])
            
            # Lê os dados atuais
            dados_atuais = conn.read()
            
            # Junta com a nova reserva
            df_final = pd.concat([dados_atuais, nova_linha], ignore_index=True)
            
            # Atualiza a planilha
            conn.update(data=df_final)
            
            st.success(f"Tudo certo, {aluno}! Sua aula foi agendada.")
            st.balloons()
