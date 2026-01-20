import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. DESIGN: ASSINATURA AMPLIADA E WHATSAPP ELEVADO
# Os ajustes de 'bottom' e 'width' atendem exatamente aos seus pedidos visuais.
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
        background-color: rgba(0, 0, 0, 0.75) !important; backdrop-filter: blur(12px);
        padding: 40px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 850px; margin: auto; text-align: center; color: white !important;
    }
    
    /* Assinatura by Andre Aranha - Aumentada em 40% no canto esquerdo */
    .assinatura-aranha {
        position: fixed;
        bottom: 25px;
        left: 25px;
        width: 160px; /* Tamanho ajustado para destaque máximo */
        z-index: 9999;
        filter: drop-shadow(2px 2px 5px rgba(0,0,0,0.8));
    }

    /* WhatsApp Flutuante - Subido em 1cm no canto direito */
    .whatsapp-float {
        position: fixed;
        bottom: 65px; /* Elevado para evitar sobreposição na base */
        right: 25px;
        width: 60px;
        z-index: 9999;
    }
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

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 4. LÓGICA DE CONTEÚDO
menu = st.session_state.pagina

# --- PÁGINA HOME: AGENDAMENTO ---
if menu == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()

            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                servico = st.selectbox("Serviço", ["Aula Individual (R$ 250/h)", "Aula em Dupla (R$ 200/pessoa)", "Aluguel de Quadra (R$ 250/h)"])
                n_horas = st.number_input("Horas", min_value=1, value=1)
                data = st.date_input("Data", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])

                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        # CORREÇÃO: data_str e DataFrame fechados corretamente para evitar Script Error
                        data_str = data.strftime("%Y-%m-%d")
                        nova_reserva = pd.DataFrame([{
                            "Data": data_str, "Horario": horario, "Aluno": aluno, 
                            "Servico": servico, "Horas": n_horas, "Status": "Pendente", "Academia": academia
                        }])
                        df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success("Reserva realizada com sucesso!")
        except Exception:
            # CORREÇÃO: String finalizada corretamente
            st.warning("Conectando ao banco de dados...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO ---
elif menu == "Cadastro":
    # CORREÇÃO: Markdown fechado corretamente
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    tipo_cad = st.radio("Selecione:", ["Aluno", "Professor", "Academia"], horizontal=True)
    
    # CORREÇÃO: Links mapeados corretamente sem inversão
    links_forms = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe src="{links_forms[tipo_cad]}" width="100%" height="800" frameborder="0" 
            style="background: white; border-radius: 20px; max-width: 850px;"></iframe>
        </div>
    """, unsafe_allow_html=True)

elif menu == "Contato":
    st.markdown('<div class="custom-card"><h3>André Aranha</h3><p>📧 aranha.corp@gmail.com.br</p></div>', unsafe_allow_html=True)
