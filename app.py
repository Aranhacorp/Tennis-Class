import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO E ESTILO PADRONIZADO
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    /* Design do Balão Cinza Transparente com Fonte Branca */
    .main-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: white !important; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-display {
        color: white !important; font-size: 34px; font-weight: bold; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }
    .stButton>button { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# 2. NAVEGAÇÃO
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
    for item in ["Home", "Serviços", "Cadastro", "Contato"]:
        if st.button(item, use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

# --- PÁGINA HOME: PAGAMENTO ---
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Pagamento</h1>", unsafe_allow_html=True)
    
    # Exemplo de valor
    st.markdown("<div class='total-display'>Total do Pacote: R$ 600,00</div>", unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Exibição do QR Code direto do seu repositório
    st.markdown("### Escaneie o QR Code")
    # Link corrigido com o nome exato do arquivo no seu GitHub
    qr_url = "https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Andre%20Aranha%20Cagno%20-%20Chave%20PIX%20Banco%20Inter.png"
    st.image(qr_url, width=280)

    # Chave PIX e Funcionalidade de Cópia
    chave_pix = "aranha.corp@gmail.com.br"
    st.markdown(f"<p style='font-size: 18px;'>Chave PIX: <b>{chave_pix}</b></p>", unsafe_allow_html=True)
    
    # Botão de cópia simplificado
    if st.button("📋 Copiar Chave PIX", use_container_width=True):
        st.code(chave_pix, language=None) # Abre campo facilitado para cópia em mobile
        st.toast("Chave PIX exibida para cópia!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.file_uploader("Anexe seu comprovante aqui", type=['png', 'jpg', 'pdf'])
    
    if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
        st.balloons()
        st.success("Enviado com sucesso!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (CORREÇÃO ALUNO/ACADEMIA) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione o tipo:", ["Aluno", "Academia", "Professor"], horizontal=True)
    
    # Links mapeados corretamente
    links = {
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true",
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINA CONTATO ---
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: white;'>André Aranha</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 20px;'>✉️ aranha.corp@gmail.com.br<br>📱 (11) 97142-5028</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
