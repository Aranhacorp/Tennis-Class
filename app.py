import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO E CONEXÃO
st.set_page_config(page_title="TENNIS CLASS", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. ESTILO CSS (PADRÃO TRANSPARENTE BRANCO)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .custom-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .text-total {
        color: white !important; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO LATERAL
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True): 
        st.session_state.pagina = "Home"; st.rerun()
    if st.button("Cadastro", use_container_width=True): 
        st.session_state.pagina = "Cadastro"; st.rerun()

# --- PÁGINA HOME ---
if st.session_state.pagina == "Home":
    if 'pagamento_ativo' not in st.session_state:
        st.session_state.pagamento_ativo = False

    if not st.session_state.pagamento_active:
        # FORMULÁRIO DE RESERVA
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            pacote = st.selectbox("Pacotes", [
                "Aula Individual Pacote 4 Aulas (R$ 235/hora)",
                "Aula Individual Pacote 8 Aulas (R$ 225/hora)",
                "Aula Kids Pacote 4 Aulas (R$ 230/hora)"
            ])
            data_aula = st.date_input("Data")
            horario = st.selectbox("Horário", ["11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"])
            
            if st.form_submit_button("CONFIRMAR RESERVA"):
                if aluno:
                    st.session_state.reserva = {
                        "Data": data_aula.strftime("%d/%m/%Y"),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Pacote": pacote,
                        "Status": "Pendente"
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else:
                    st.error("Por favor, preencha o nome do aluno.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # TELA DE PAGAMENTO (SEM QR CODE)
        st.markdown(f"<div class='text-total'>Total do Pacote: {st.session_state.reserva['Pacote']}</div>", unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        st.write("### Copie a chave PIX para finalizar")
        chave_pix = "aranha.corp@gmail.com.br"
        st.code(chave_pix, language=None) # Função de cópia automática
        
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        if st.button("FINALIZAR E SALVAR", type="primary", use_container_width=True):
            try:
                # ATUALIZAÇÃO DA PLANILHA
                df_atual = conn.read(worksheet="Página1")
                novo_registro = pd.DataFrame([st.session_state.reserva])
                df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                
                st.balloons()
                st.success("Pagamento confirmado e dados salvos na TennisClass_DB!")
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao conectar com a planilha: {e}")
        
        if st.button("Voltar"):
            st.session_state.pagamento_ativo = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    st.markdown(f'<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true" width="100%" height="800" frameborder="0" style="background:white; border-radius:15px;"></iframe>', unsafe_allow_html=True)
