import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="SPORTS CLASS", layout="centered")

# 2. CSS para o fundo e estilo
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        margin-top: 20px;
    }
    
    .pix-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #003366;
        text-align: center;
        margin-top: 20px;
    }
    
    h1 {
        color: white;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px #000000;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1>SPORTS CLASS 🎾</h1>', unsafe_allow_html=True)

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
        horario = st.selectbox("Horário", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"])
        
        submit = st.form_submit_button("CONFIRMAR E IR PARA PAGAMENTO")
        
        if submit:
            if aluno:
                try:
                    # Salva na planilha
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
                    
                    # Mensagem de sucesso e ativação da tela de pagamento
                    st.success(f"Reserva pré-agendada, {aluno}!")
                    st.session_state['pago'] = True
                    st.session_state['aluno_nome'] = aluno
                    st.balloons()
                except Exception as e:
                    st.error("Erro ao salvar. Verifique as permissões da planilha.")
            else:
                st.warning("Por favor, preencha o nome.")

    # --- ETAPA DE PAGAMENTO ---
    if 'pago' in st.session_state:
        st.markdown("---")
        st.markdown('<div class="pix-box">', unsafe_allow_html=True)
        st.markdown(f"### 💰 Pagamento via PIX")
        st.write(f"Para confirmar sua vaga, realize o pagamento do **{servico}**")
        
        # Coloque sua chave PIX aqui
        st.code("250.197.278-30 (Pode ser CPF, E-mail ou Celular)", language="text")
        
        st.write("**Instruções:**")
        st.write("1. Copie a chave acima e pague no seu banco.")
        st.write("2. Envie o comprovante para o WhatsApp: **(11) 97142-5028**")
        st.write("3. Sua reserva será confirmada após o envio do comprovante.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
