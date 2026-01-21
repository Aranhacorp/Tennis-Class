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
    .custom-card, .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: white !important; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-pagamento {
        color: white !important; font-size: 32px; font-weight: bold; 
        text-align: center; margin-bottom: 20px;
    }
    /* Estilo para inputs dentro do card escuro */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
    
    for item in ["Home", "Serviços", "Cadastro", "Contato"]:
        if st.button(item, use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

# --- PÁGINA HOME: PAGAMENTO ---
if st.session_state.pagina == "Home":
    st.markdown("<h1 style='text-align: center; color: white;'>Finalizar Reserva</h1>", unsafe_allow_html=True)
    
    # Exemplo de valor capturado (ajuste conforme seu fluxo)
    total_exemplo = 600.00 
    st.markdown(f"<div class='total-pagamento'>Total do Pacote: R$ {total_exemplo:.2f}</div>", unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # QR Code
    st.markdown("### Escaneie o QR Code para pagar")
    try:
        # Tenta carregar a imagem do repositório
        st.image("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/QRCode_PIX.png", width=250)
    except:
        st.error("Imagem do QR Code não encontrada no GitHub. Verifique o nome do arquivo.")

    # Chave PIX com funcionalidade de cópia
    chave_pix = "aranha.corp@gmail.com.br"
    st.markdown(f"**Chave PIX (E-mail):** `{chave_pix}`")
    if st.button("📋 Copiar Chave PIX"):
        st.write(f'<script>navigator.clipboard.writeText("{chave_pix}");</script>', unsafe_allow_html=True)
        st.toast("Chave copiada com sucesso!")

    st.markdown("---")
    st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
    
    if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
        st.success("Pagamento enviado para análise!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (CORREÇÃO DE LINKS) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione:", ["Aluno", "Academia", "Professor"], horizontal=True)
    
    # Links corrigidos para não ficarem trocados
    links = {
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true",
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:15px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINA CONTATO ---
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="contact-card">', unsafe_allow_html=True)
    st.markdown("## André Aranha")
    st.markdown("📧 aranha.corp@gmail.com.br")
    st.markdown("📱 (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)
