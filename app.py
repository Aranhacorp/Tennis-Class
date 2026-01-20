import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. ESTILIZAÇÃO CSS (CORREÇÃO DE ASPAS)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .custom-card {
        background-color: rgba(0, 0, 0, 0.75) !important; backdrop-filter: blur(10px);
        padding: 30px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 850px; margin: auto; color: white !important;
    }
    </style>
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

# 4. LÓGICA DAS ABAS
menu = st.session_state.pagina

if menu == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read() #

            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                precos = {
                    "Aula Individual": 250,
                    "Aula em Dupla": 200,
                    "Aluguel de Quadra": 250
                }
                servico = st.selectbox("Serviço", list(precos.keys()))
                n_horas = st.number_input("Número de Horas", min_value=1, value=1)
                data = st.date_input("Data", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])

                if st.form_submit_button("CONFIRMAR RESERVA"):
                    data_str = data.strftime("%Y-%m-%d")
                    
                    # BLOQUEIO DE HORÁRIO
                    conflito = df_base[(df_base['Data'].astype(str) == data_str) & 
                                      (df_base['Horario'].astype(str) == horario)]
                    
                    if not conflito.empty:
                        st.error(f"❌ Horário {horario} ocupado em {data.strftime('%d/%m/%Y')}.")
                    elif not aluno:
                        st.warning("Preencha o nome do aluno.")
                    else:
                        # CÁLCULO DE VALOR
                        valor_total = precos[servico] * n_horas
                        nova_linha = pd.DataFrame([{
                            "Data": data_str, "Horario": horario, "Aluno": aluno, 
                            "Servico": servico, "Horas": n_horas, "Valor": valor_total, 
                            "Status": "Pendente", "Academia": academia
                        }])
                        df_final = pd.concat([df_base, nova_linha], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success("Reserva realizada!")
        except:
            st.error("Erro ao conectar com a planilha TennisClass_DB.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Cadastro":
    st.markdown("<h3 style='text-align: center; color: white;'>Seleção de Cadastro</h3>", unsafe_allow_html=True)
    
    # 3 ETAPAS DE CADASTRO
    tipo = st.radio("Selecione quem deseja cadastrar:", ["Aluno", "Professor", "Academia"], horizontal=True)
    
    # Links dos Forms (Ajuste conforme seus formulários)
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true"
    }

    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe src="{links[tipo]}" width="100%" height="800" frameborder="0" marginheight="0" marginwidth="0" 
            style="background: white; border-radius: 15px; max-width: 850px;">
            Carregando formulário de {tipo}...</iframe>
        </div>
    """, unsafe_allow_html=True)

elif menu == "Contato":
    st.markdown('<div class="custom-card"><h3>André Aranha</h3><p>📞 11 97142 5028</p></div>', unsafe_allow_html=True)
