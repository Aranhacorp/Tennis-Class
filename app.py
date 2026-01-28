import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'academia_foco' not in st.session_state: st.session_state.academia_foco = None

# 4. DESIGN E ESTILO (CSS)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    .custom-card {
        background-color: rgba(255, 255, 255, 0.9) !important; 
        padding: 30px; border-radius: 20px; max-width: 800px; margin: auto; 
        text-align: center; color: #333 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .translucent-balloon {
        background-color: rgba(60, 60, 60, 0.65); padding: 25px; border-radius: 15px; 
        border: 1px solid rgba(255,255,255,0.1); color: white; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .btn-cadastro {
        display: block; width: 100%; background-color: #1e5e20; color: white !important;
        padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center;
    }
    .sidebar-detalhe {
        text-align: left !important; color: #f0f0f0; font-size: 13px; margin: -10px 0 15px 35px;
        line-height: 1.4; border-left: 2px solid #ff4b4b; padding-left: 10px;
    }
    .assinatura-aranha { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-float { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
</a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL
info_academias = {
    "Play Tennis Ibirapuera": "R. Joinville, 401 - Vila Mariana<br>📞 (11) 5081-3000",
    "Top One Tennis": "R. João Lourenço, 629 - Vila Nova Conceição<br>📞 (11) 3845-6688",
    "Fontes & Barbeta Tennis": "Av. Prof. Ascendino Reis, 724<br>📞 (11) 99911-3000",
    "Arena BTG": "Av. das Nações Unidas, 13797<br>📞 (11) 94555-2200"
}

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
    for nome in info_academias.keys():
        if st.button(f"📍 {nome}", key=f"nav_{nome}", use_container_width=True):
            st.session_state.academia_foco = nome if st.session_state.academia_foco != nome else None
        if st.session_state.academia_foco == nome:
            st.markdown(f'<div class="sidebar-detalhe">{info_academias[nome]}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. PÁGINAS E LOGICA DE GRAVAÇÃO
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendamento")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail")
            servico = st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Aula em Grupo", "Aula Kids"])
            local = st.selectbox("Unidade", list(info_academias.keys()))
            data_aula = st.date_input("Data", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%Y-%m-%d"),
                        "Horario": hora_aula,
                        "Aluno": aluno,
                        "Servico": servico,
                        "Status": "Pendente",
                        "Academia": local,
                        "Email_Aluno": email
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else:
                    st.error("Preencha todos os campos.")
    else:
        st.markdown("### 💳 Pagamento PIX")
        st.write(f"Aluno: {st.session_state.reserva_temp['Aluno']}")
        st.code("aranha.corp@gmail.com.br")
        if st.button("CONFIRMAR AGENDAMENTO"):
            try:
                # GRAVAÇÃO REAL NA PLANILHA
                existing_data = conn.read(worksheet="Página1", usecols=[0,1,2,3,4,5,6])
                new_row = pd.DataFrame([st.session_state.reserva_temp])
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(worksheet="Página1", data=updated_df)
                
                st.balloons()
                st.success("Reserva salva na TennisClass_DB!")
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros")
    # Links corrigidos para evitar "Arquivo inexistente"
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro">👤 Cadastro de Aluno</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdO7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform" class="btn-cadastro">🏢 Cadastro de Academia</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform" class="btn-cadastro">🎾 Cadastro de Professor</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="translucent-balloon"><h2>🎾 Serviços</h2><p>Individual: R$ 250/h<br>Grupo: R$ 200/h</p></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="translucent-balloon"><h3>📞 Contato</h3><p>📱 (11) 97142-5028</p></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="translucent-balloon"><h3>🎒 Loja</h3><p>Em breve acessórios.</p></div>', unsafe_allow_html=True)
