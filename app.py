import streamlit as st

# 1. CONFIGURAÇÃO E ESTILO PADRONIZADO
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    /* Balão cinza com transparência e fonte branca */
    .pix-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 30px; border-radius: 20px; 
        max-width: 600px; margin: auto; text-align: center; 
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-titulo {
        color: white !important; font-size: 30px; font-weight: bold; 
        text-align: center; margin-bottom: 20px;
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
    
    # Exemplo de total capturado
    st.markdown("<div class='total-titulo'>Total do Pacote: R$ 600,00</div>", unsafe_allow_html=True)

    st.markdown('<div class="pix-card">', unsafe_allow_html=True)
    
    st.markdown("### Escaneie o QR Code para pagar")
    # Link direto para o arquivo exato no seu repositório GitHub
    qr_url = "https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Andre%20Aranha%20Cagno%20-%20Chave%20PIX%20Banco%20Inter.png"
    st.image(qr_url, width=250)

    # Chave PIX e funcionalidade de cópia
    chave_pix = "aranha.corp@gmail.com.br"
    st.markdown(f"**Chave PIX:** `{chave_pix}`")
    
    # Botão de cópia nativo do Streamlit para maior compatibilidade
    if st.button("📋 Clique para copiar a chave PIX", use_container_width=True):
        st.code(chave_pix, language=None)
        st.success("Chave disponível acima para copiar!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
    
    if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
        st.balloons()
        st.success("Reserva enviada! Aguarde a confirmação.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (CORREÇÃO DE LINKS) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione:", ["Aluno", "Academia", "Professor"], horizontal=True)
    
    # Mapeamento corrigido para não haver trocas
    links = {
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true",
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:15px;"></iframe>', unsafe_allow_html=True)
