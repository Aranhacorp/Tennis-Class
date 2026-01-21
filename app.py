import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS: CARD BRANCO, ASSINATURA AMPLIADA E WHATSAPP ELEVADO
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
    
    /* Card BRANCO para o conteúdo central */
    .custom-card {
        background-color: rgba(255, 255, 255, 0.95) !important; 
        backdrop-filter: blur(10px);
        padding: 40px; border-radius: 25px; 
        border: 1px solid rgba(0, 0, 0, 0.1);
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important;
    }
    
    .service-item {
        background: rgba(0, 0, 0, 0.05); padding: 12px; border-radius: 12px;
        margin: 8px 0; border: 1px solid rgba(0, 0, 0, 0.1);
        font-size: 1.1rem; color: #1E1E1E; text-align: left;
    }
    
    /* Assinatura "by Andre Aranha" (Canto Inferior Esquerdo) */
    .assinatura-aranha {
        position: fixed; bottom: 25px; left: 25px;
        width: 180px; z-index: 9999;
        filter: drop-shadow(2px 2px 5px rgba(0,0,0,0.8));
    }
    
    /* WhatsApp elevado (Canto Inferior Direito) */
    .whatsapp-float {
        position: fixed; bottom: 70px; right: 25px;
        width: 60px; z-index: 9999;
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

menu = st.session_state.pagina

# --- PÁGINA HOME: AGENDAMENTO COM ORDEM ESPECÍFICA ---
if menu == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()
            with st.form("agendamento"):
                st.markdown("<p style='color: #1E1E1E; font-weight: bold;'>Reserve seu horário:</p>", unsafe_allow_html=True)
                aluno = st.text_input("Nome do Aluno")
                
                # DICIONÁRIO NA ORDEM SOLICITADA
                pacotes_opcoes = {
                    "Aula Individual Pacote 4 Aulas (R$ 235/hora)": 235,
                    "Aula Individual Pacote 8 Aulas (R$ 225/hora)": 225,
                    "Aula Individual Única (R$ 250/hora)": 250,
                    "Aula Kids Pacote 4 Aulas (R$ 230/hora)": 230,
                    "Aula em Grupo até 3 pessoas (R$ 200/hora)": 200,
                    "Locação de Quadra (Valor a Consultar)": 0,
                    "Eventos (Valor a Consultar)": 0
                }
                
                pacote_selecionado = st.selectbox("Pacotes", list(pacotes_opcoes.keys()))
                n_horas = st.number_input("Quantidade (Horas ou Sessões)", min_value=1, value=1)
                data = st.date_input("Data")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                
                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        data_str = data.strftime("%Y-%m-%d")
                        v_unit = pacotes_opcoes[pacote_selecionado]
                        total = v_unit * n_horas if v_unit > 0 else "A Consultar"
                        
                        nova_reserva = pd.DataFrame([{
                            "Data": data_str, "Horario": horario, "Aluno": aluno, 
                            "Pacote": pacote_selecionado, "Qtd": n_horas, "Total": total, "Status": "Pendente"
                        }])
                        df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success(f"Reserva enviada com sucesso!")
        except:
            st.info("Conectando ao banco de dados...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA SERVIÇOS ---
elif menu == "Serviços":
    st.markdown("<h2 style='text-align: center; color: white;'>Nossos Serviços</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        # LISTA DE SERVIÇOS EM ITENS SCANNABLE
        servicos_display = [
            "🎾 Aulas Particulares (Individuais)",
            "👥 Aulas em Grupo (Até 3 pessoas)",
            "👶 Aula Kids (Metodologia Adaptada)",
            "🏟️ Locação de Quadra",
            "🎤 Palestras e Workshop",
            "💪 Treinamento Esportivo (Fitness focado em Tênis)",
            "🏆 Clínicas e Eventos Corporativos",
            "🎾 Esportivas com Tênis"
        ]
        for s in servicos_display:
            st.markdown(f'<div class="service-item">{s}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO ---
elif menu == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    tipo_cad = st.radio("Selecione:", ["Aluno", "Professor", "Academia"], horizontal=True)
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[tipo_cad]}" width="100%" height="800" frameborder="0" style="background:white;
