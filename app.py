import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

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
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(15px);
    }
    </style>
""", unsafe_allow_html=True)

# 2. CONTROLE DE NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 3. LÓGICA DE CONTEÚDO
menu = st.session_state.pagina

# --- PÁGINA HOME (AGENDAMENTO + BLOQUEIO) ---
if menu == "Home":
    st.markdown("<h2 style='text-align: center; color: white;'>Agendamento Profissional</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read() # Conexão com TennisClass_DB

            with st.form("form_reserva"):
                aluno = st.text_input("Nome do Aluno")
                precos = {
                    "Aula Individual (R$ 250/h)": 250,
                    "Aula em Dupla (R$ 200/pessoa)": 200,
                    "Aluguel de Quadra (R$ 250/h)": 250
                }
                servico = st.selectbox("Serviço", list(precos.keys()))
                n_horas = st.number_input("Horas", min_value=1, max_value=5, value=1)
                data = st.date_input("Data", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])

                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if not aluno:
                        st.error("Por favor, preencha o nome do aluno.")
                    else:
                        data_str = data.strftime("%Y-%m-%d")
                        # LÓGICA DE BLOQUEIO: Verifica se já existe reserva para Data + Horário
                        conflito = df_base[(df_base['Data'].astype(str) == data_str) & 
                                          (df_base['Horario'].astype(str) == horario)]
                        
                        if not conflito.empty:
                            st.error(f"❌ O horário {horario} no dia {data.strftime('%d/%m/%Y')} já está ocupado.")
                        else:
                            # CÁLCULO FINANCEIRO AUTOMÁTICO
                            valor_total = precos[servico] * n_horas
                            
                            nova_reserva = pd.DataFrame([{
                                "Data": data_str, "Horario": horario, "Aluno": aluno, 
                                "Servico": servico, "Horas": n_horas, "Valor": valor_total, 
                                "Status": "Pendente", "Academia": academia
                            }])
                            
                            df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                            conn.update(data=df_final)
                            st.balloons()
                            st.session_state.sucesso = True
                            st.rerun()

            if st.session_state.get('sucesso'):
                st.success("Reserva realizada com sucesso!")
                qr = segno.make("25019727830")
                img_buffer = BytesIO()
                qr.save(img_buffer, kind='png', scale=5)
                st.image(img_buffer.getvalue(), width=180, caption="PIX para Agendamento")
                st.code("Chave PIX: 250.197.278-30")
        except:
            st.warning("Aguardando conexão com o banco de dados...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (3 FORMS INTEGRADOS) ---
elif menu == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    
    # Seletor de Categoria
    tipo_cad = st.radio(
        "Quem você deseja cadastrar?",
        ["Aluno", "Professor", "Academia"],
        horizontal=True
    )
    
    # Dicionário de Links (Substitua os links temporários pelos seus links reais)
    links_forms = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true", # Substituir pelo link do Aluno
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true" # Substituir pelo link da Academia
    }
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe src="{links_forms[tipo_cad]}" width="100%" height="900" frameborder="0" marginheight="0" marginwidth="0" 
            style="background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 850px;">
            Carregando formulário...</iframe>
        </div>
    """, unsafe_allow_html=True)

# --- PÁGINA CONTATO ---
elif menu == "Contato":
    st.markdown("""
        <div class="custom-card">
            <h2>André Aranha</h2>
            <p>📧 aranha.corp@gmail.com.br</p>
            <p>📞 11 - 97142 5028</p>
            <br>
            <a href="https://wa.me/5511971425028" target="_blank" 
               style="background:#25d366; color:white; padding:15px 30px; border-radius:12px; text-decoration:none; font-weight:bold;">
               WHATSAPP DIRETO
            </a>
        </div>
    """, unsafe_allow_html=True)
