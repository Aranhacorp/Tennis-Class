import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. DESIGN E ESTILO (CSS)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 55px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }
    .custom-card {
        background-color: rgba(255, 255, 255, 0.98) !important; 
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    /* Balão de Contato Cinza Transparente */
    .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 45px; border-radius: 30px;
        max-width: 650px; margin: 40px auto; text-align: center;
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .total-pagamento {
        color: white !important; font-size: 36px; font-weight: bold; 
        margin: 25px 0; text-shadow: 3px 3px 5px rgba(0,0,0,0.5);
        text-align: center;
    }
       .pix-info {
        background-color: #f0f2f6; border: 2px dashed #007bff;
        padding: 20px; border-radius: 15px; margin: 20px 0; color: #1E1E1E;
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias Recomendadas</h3>", unsafe_allow_html=True)
    academias = {
        "Play Tennis Ibirapuera": {"End": "Rua Estado de Israel, 860", "Tel": "11-97752-0488"},
        "Top One tennis": {"End": "Avenida Indianapolis, 647", "Tel": "11-93236-3828"},
        "Fontes & Barbeta Tennis": {"End": "Rua Oscar Gomes Cardim, 535", "Tel": "11-94695-3738"},
        "Arena BTG": {"End": "Rua Major Sylvio de Magalhães Padilha, 16741", "Tel": "11-98854-3860"}
    }
    for nome, info in academias.items():
        with st.expander(nome):
            st.write(f"📍 {info['End']}")
            st.write(f"📞 {info['Tel']}")

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# --- PÁGINA HOME: AGENDAMENTO ---
if st.session_state.pagina == "Home":
    if 'pagamento_ativo' not in st.session_state:
        st.session_state.pagamento_ativo = False

    if not st.session_state.pagamento_ativo:
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            with st.form("form_reserva"):
                aluno = st.text_input("Nome do Aluno")
                opcoes_pacotes = {
                    "Aula Individual Pacote 4 Aulas (R$ 235/h)": 940,
                    "Aula Individual Pacote 8 Aulas (R$ 225/h)": 1800,
                    "Aula Individual Única (R$ 250/h)": 250,
                    "Aula Kids Pacote 4 Aulas (R$ 230/h)": 920,
                    "Aula em Grupo até 3 pessoas (R$ 200/h)": 600,
                    "Locação de Quadra (Valor a Consultar)": 0,
                    "Eventos (Valor a Consultar)": 0
                }
                pacote_sel = st.selectbox("Selecione o Pacote", list(opcoes_pacotes.keys()))
                data_input = st.date_input("Escolha a Data", format="DD/MM/YYYY") #
                horario = st.selectbox("Escolha o Horário", [f"{h:02d}:00" for h in range(11, 22)])
                
                if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                    if aluno:
                        st.session_state.reserva_temp = {
                            "Aluno": aluno, "Pacote": pacote_sel,
                            "Data": data_input.strftime("%d/%m/%Y"), 
                            "Horario": horario, "Total": opcoes_pacotes[pacote_sel]
                        }
                        st.session_state.pagamento_ativo = True
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # ETAPA DE PAGAMENTO COM QR CODE
        res = st.session_state.reserva_temp
        st.markdown(f"<div class='total-pagamento'>Total do Pacote: R$ {res['Total']:.2f}</div>", unsafe_allow_html=True if res['Total'] > 0 else "")
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### Escaneie o QR Code para pagar")
            # Inserção do QR Code (Substitua pela URL real da sua imagem de QR Code)
            st.image("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/QRCode_PIX.png", width=250)
            
            st.markdown(f'<div class="pix-info"><b>Chave PIX:</b> aranha.corp@gmail.com.br<br><b>Favorecido:</b> André Aranha</div>', unsafe_allow_html=True)
            st.file_uploader("Anexe o comprovante aqui", type=['png', 'jpg', 'pdf'])
            
            if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
                st.balloons()
                st.success("Tudo pronto! Sua reserva foi enviada.")
                st.session_state.pagamento_ativo = False
            st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA SERVIÇOS (RESTAURADA) ---
elif st.session_state.pagina == "Serviços":
    st.markdown("<h2 style='text-align: center; color: white;'>Nossos Serviços</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🎾 Tênis & Aulas")
            st.write("- **Aula Particular:** Personalizada para seu nível.")
            st.write("- **Aula Kids:** Iniciação esportiva divertida.")
            st.write("- **Grupo:** Dinâmica e socialização.")
        with col2:
            st.markdown("### 🏢 Infraestrutura")
            st.write("- **Locação:** Quadras de saibro e rápida.")
            st.write("- **Eventos:** Torneios e clínicas.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (CORREÇÃO ALUNO X ACADEMIA) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione o perfil desejado:", ["Aluno", "Professor", "Academia"], horizontal=True)
    
    # Mapeamento corrigido
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINA CONTATO (DESIGN CINZA PADRÃO) ---
elif st.session_state.pagina == "Contato":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="contact-card">
            <h1 style="color: white; margin-bottom: 10px;">André Aranha</h1>
            <p style="font-size: 20px; color: white;">
                ✉️ aranha.corp@gmail.com.br<br>
                📱 (11) 97142-5028
            </p>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 25px 0;">
            <p style="font-size: 14px; color: rgba(255,255,255,0.6);">
                TENNIS CLASS © 2026
            </p>
        </div>
    """, unsafe_allow_html=True)

