import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. INICIALIZAÇÃO DO ESTADO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 4. DESIGN E ESTILO (CSS) - RESTAURANDO O BALÃO CINZA TRANSPARENTE
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
    /* BALÃO DE CONTATO CINZA TRANSPARENTE PADRÃO */
    .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 45px; border-radius: 30px;
        max-width: 650px; margin: 40px auto; text-align: center;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL E ACADEMIAS
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
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

# 6. PÁGINA HOME (AGENDAMENTO + SALVAMENTO DB)
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            pacotes = {
                "Aula Individual Única (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940, 
                "Pacote 8 Aulas (R$ 1800)": 1800,
                "Aula Kids - 4 Aulas (R$ 920)": 920,
                "Grupo até 3 pessoas (R$ 600)": 600
            }
            pacote_sel = st.selectbox("Selecione o Pacote", list(pacotes.keys()))
            data_sel = st.date_input("Escolha a Data")
            hora_sel = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_sel.strftime("%d/%m/%Y"),
                        "Horario": hora_sel,
                        "Aluno": aluno,
                        "Servico": "Aula",
                        "Pacote": pacote_sel,
                        "Status": "Pendente",
                        "Academia": ""
                    }
                    st.session_state.total_valor = pacotes[pacote_sel]
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h2 style='text-align: center; color: white;'>Total: R$ {st.session_state.total_valor:.2f}</h2>", unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write("### 💳 Pagamento via PIX")
        st.code("aranha.corp@gmail.com.br", language=None)
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar", use_container_width=True):
                st.session_state.pagamento_ativo = False
                st.rerun()
        with col2:
            if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
                try:
                    df_atual = conn.read(worksheet="Página1")
                    nova_linha = pd.DataFrame([st.session_state.reserva_temp])
                    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_final)
                    st.balloons()
                    st.success("Agendamento salvo na TennisClass_DB!")
                    st.session_state.pagamento_ativo = False
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# 7. PÁGINA SERVIÇOS (RESTAURADA COM ITENS QUE SUMIRAM)
elif st.session_state.pagina == "Serviços":
    st.markdown("<h2 style='text-align: center; color: white;'>Nossos Serviços</h2>", unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎾 Tênis & Aulas")
        st.write("- **Aula Particular:** Focada no seu desenvolvimento técnico.") [cite: 59]
        st.write("- **Aula Kids:** Metodologia lúdica para crianças.") [cite: 59]
        st.write("- **Aula em Dupla/Grupo:** Socialização e dinâmica de jogo.") [cite: 59]
    with col2:
        st.markdown("### 🏢 Infraestrutura & Gestão")
        st.write("- **Locação de Quadras:** Saibro e Rápida.") [cite: 59]
        st.write("- **Clínicas de Tênis:** Intensivos de final de semana.") [cite: 60]
        st.write("- **Gestão de Academias:** Consultoria para condomínios e clubes.") [cite: 60]
    st.markdown('</div>', unsafe_allow_html=True)

# 8. PÁGINA CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione o perfil:", ["Aluno", "Professor", "Academia"], horizontal=True)
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

# 9. PÁGINA CONTATO (BALÃO CINZA TRANSPARENTE RESTAURADO)
elif st.session_state.pagina == "Contato":
    st.markdown("""
        <div class="contact-card">
            <h1 style="color: white; margin-bottom: 10px;">André Aranha</h1>
            <p style="font-size: 22px; color: white;">
                ✉️ aranha.corp@gmail.com.br<br>
                📱 (11) 97142-5028
            </p>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 25px 0;">
            <p style="font-size: 14px; color: rgba(255,255,255,0.6);">
                TENNIS CLASS © 2026
            </p>
        </div>
    """, unsafe_allow_html=True) [cite: 62, 66]
