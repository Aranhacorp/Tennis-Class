import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="TENNIS CLASS", layout="centered")

# 2. CSS para o fundo, card e alinhamento do logotipo
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

    .logo-img {
        border-radius: 10px;
        mix-blend-mode: screen; 
    }

    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho com Título e Imagem Lateral
st.markdown(f"""
    <div class="header-container">
        <h1>TENNIS CLASS</h1>
        <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/tennis-player-silhouette%20ver2.jpg" width="70" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

st.markdown('<h3 style="text-align: center; color: white; text-shadow: 1px 1px 2px #000; margin-bottom: 20px;">Agendamento Profissional</h3>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📝 Agende sua Aula")
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        st.error("Erro na conexão com a planilha.")

    with st.form("agendamento"):
        aluno = st.text_input("Nome do Aluno")
        servico = st.selectbox("Selecione o Serviço", [
            "Aula Individual (R$ 250)", 
            "Aula em Dupla (R$ 200/pessoa)", 
            "Aluguel de Quadra (R$ 250)"
        ])
        
        data = st.date_input("Data Desejada")
        
        # --- Lógica de Horários (Segunda a Sexta) ---
        dia_semana = data.weekday() 
        
        if dia_semana == 0:  # SEGUNDA
            lista_horarios = ["12:00", "13:00", "15:00"]
        elif dia_semana == 1: # TERÇA
            lista_horarios = ["11:00", "12:00", "13:00", "14:00", "15:00"]
        elif dia_semana == 2: # QUARTA
            lista_horarios = ["12:00", "14:00", "16:00", "18:00"]
        elif dia_semana == 3: # QUINTA
            lista_horarios = ["10:00", "12:00", "15:00", "17:00", "19:00"]
        elif dia_semana == 4: # SEXTA
            lista_horarios = ["10:00", "12:00", "15:00", "16:00", "18:00", "20:00"]
        else: # FINAIS DE SEMANA
            lista_horarios = ["08:00", "09:00", "10:00", "11:00"]
            
        horario = st.selectbox("Horário Disponível", lista_horarios)
        
        submit = st.form_submit_button("CONFIRMAR E IR PARA PAGAMENTO")
        
        if submit:
            if aluno:
                try:
                    nova_linha = pd.DataFrame([{
                        "Data": str(data),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Servico": servico,
                        "Status": "Aguardando Pagamento"
                    }])
                    dados_existentes = conn.read()
                    df_final = pd.concat([dados_existentes, nova_linha], ignore_index=True)
                    conn.update(data=df_final)
                    
                    st.session_state['pago'] = True
                    st.session_state['servico_selecionado'] = servico
                    st.success(f"Reserva pré-agendada para {aluno}!")
                    st.balloons()
                except Exception as e:
                    st.error("Erro ao salvar dados na planilha.")
            else:
                st.warning("Por favor, preencha o nome do aluno.")

    # --- ETAPA DE PAGAMENTO (CORRIGIDA) ---
    if st.session_state.get('pago'):
        st.markdown("---")
        st.markdown('<div style="text-align: center; background-color: #f0f8ff; padding: 20px; border-radius: 10px; border: 2px dashed #003366;">', unsafe_allow_html=True)
        st.markdown("### 💰 Pagamento via PIX")
        st.write(f"Valor referente a: **{st.session_state.get('servico_selecionado')}**")
        st.code("250.197.278-30", language="text")
        st.write("Envie o comprovante para o WhatsApp: **(11) 97142-5028**")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
