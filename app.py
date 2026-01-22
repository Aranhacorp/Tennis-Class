import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    /* Balão cinza com transparência e fonte branca */
    .custom-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: white !important; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-text {
        color: white !important; font-size: 32px; font-weight: bold; 
        text-align: center; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE NAVEGAÇÃO (IMPEDE O SUMIÇO DAS PÁGINAS)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True):
        st.session_state.pagina = "Home"
        st.rerun()
    if st.button("Serviços", use_container_width=True):
        st.session_state.pagina = "Serviços"
        st.rerun()
    if st.button("Cadastro", use_container_width=True):
        st.session_state.pagina = "Cadastro"
        st.rerun()
    if st.button("Contato", use_container_width=True):
        st.session_state.pagina = "Contato"
        st.rerun()

# --- PÁGINA HOME: PAGAMENTO ---
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Finalizar Reserva</h1>", unsafe_allow_html=True)
    
    # Valor fixado para o exemplo
    st.markdown("<div class='total-text'>Total do Pacote: R$ 600,00</div>", unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # QR Code Corrigido (Caminho completo do repositório)
    st.markdown("### Escaneie o QR Code para pagar")
    qr_url = "https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Andre%20Aranha%20Cagno%20-%20Chave%20PIX%20Banco%20Inter.png"
    st.image(qr_url, width=250)

    # Chave PIX e Funcionalidade de Cópia
    chave_pix = "aranha.corp@gmail.com.br"
    st.markdown(f"**Chave PIX:**")
    st.code(chave_pix, language=None) # Gera o ícone de cópia automático do Streamlit
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
    
    if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
        st.balloons()
        st.success("Pagamento enviado! Aguarde a confirmação.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (LINKS CORRIGIDOS) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione:", ["Aluno", "Academia", "Professor"], horizontal=True)
    
    # Links mapeados corretamente
    links = {
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true",
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:15px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINA CONTATO ---
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## André Aranha")
    st.markdown("📧 aranha.corp@gmail.com.br")
    st.markdown("📱 (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)
