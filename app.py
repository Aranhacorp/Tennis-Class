import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. ESTILO CSS (PADRÃO CINZA TRANSPARENTE + FONTE BRANCA)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }
    /* Balão cinza com transparência e fonte branca */
    .custom-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: white !important; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .total-pagamento {
        color: white !important; font-size: 36px; font-weight: bold; 
        margin: 20px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .pix-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 10px; margin: 15px 0;
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 3. CONTROLE DE NAVEGAÇÃO (CORRIGIDO)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("🏠 Home", use_container_width=True): st.session_state.pagina = "Home"; st.rerun()
    if st.button("🎾 Serviços", use_container_width=True): st.session_state.pagina = "Serviços"; st.rerun()
    if st.button("📋 Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"; st.rerun()
    if st.button("📞 Contato", use_container_width=True): st.session_state.pagina = "Contato"; st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# --- PÁGINA HOME: AGENDAMENTO E PAGAMENTO ---
if st.session_state.pagina == "Home":
    if 'pagamento_ativo' not in st.session_state:
        st.session_state.pagamento_ativo = False

    if not st.session_state.pagamento_ativo:
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
            data_input = st.date_input("Escolha a Data", format="DD/MM/YYYY")
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
                else:
                    st.error("Por favor, preencha o nome.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # TELA DE PAGAMENTO
        res = st.session_state.reserva_temp
        st.markdown(f"<div class='total-pagamento' style='text-align: center;'>Total: R$ {res['Total']:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### Escaneie o QR Code")
        
        # QR Code Corrigido
        qr_url = "https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Andre%20Aranha%20Cagno%20-%20Chave%20PIX%20Banco%20Inter.png"
        st.image(qr_url, width=250)

        # Chave PIX e Cópia
        chave_pix = "aranha.corp@gmail.com.br"
        st.markdown(f"<div class='pix-box'>Chave PIX: <b>{chave_pix}</b></div>", unsafe_allow_html=True)
        if st.button("📋 Copiar Chave PIX"):
            st.code(chave_pix, language=None)
            st.toast("Chave PIX pronta para cópia!")

        arquivo = st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("VOLTAR"): 
                st.session_state.pagamento_ativo = False
                st.rerun()
        with col2:
            if st.button("CONFIRMAR AGENDAMENTO", type="primary"):
                if arquivo:
                    st.balloons()
                    st.success("Reserva Confirmada!")
                    st.session_state.pagamento_ativo = False
                else:
                    st.warning("Por favor, anexe o comprovante.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA SERVIÇOS ---
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## Nossos Serviços")
    st.write("🎾 Aula Particular Individual")
    st.write("🎾 Aula Kids (Lúdica)")
    st.write("🎾 Aula em Grupo (até 3 pessoas)")
    st.write("🏢 Locação de Quadras")
    st.write("🏢 Eventos e Clínicas")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (LINKS CORRIGIDOS) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align:center; color:white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione:", ["Aluno", "Academia", "Professor"], horizontal=True)
    
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
