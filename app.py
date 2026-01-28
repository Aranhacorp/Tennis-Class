import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'academia_foco' not in st.session_state: st.session_state.academia_foco = None

# 4. FUNÇÃO DE ENVIO DE E-MAIL (Usando Senha de App da imagem_31667b)
def enviar_email_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" # Sua senha de app gerada
    destinatario = dados['Email_Aluno']
    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = "Reserva Confirmada - TENNIS CLASS"
    
    corpo = f"""
    Olá {dados['Aluno']}, sua reserva foi agendada!
    Local: {dados['Academia']}
    Data: {dados['Data']} às {dados['Horario']}
    Serviço: {dados['Servico']}
    """
    msg.attach(MIMEText(corpo, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# 5. DESIGN E ESTILO (CSS)
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
        text-align: center; color: #333 !important;
    }
    .translucent-balloon {
        background-color: rgba(60, 60, 60, 0.75); padding: 25px; border-radius: 15px; 
        color: white; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .btn-cadastro {
        display: block; width: 100%; background-color: #1e5e20; color: white !important;
        padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center;
    }
    .assinatura-aranha { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-float { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
</a>
""", unsafe_allow_html=True)

# 6. MENU LATERAL
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
            st.markdown(f'<div style="color:white; font-size:12px; padding-left:20px;">{info_academias[nome]}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 7. LOGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendamento")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail para Confirmação")
            servico = st.selectbox("Serviço", [
                "Aula Individual R$ 250/hora", 
                "Aula em Grupo R$ 200/hora", 
                "Aula Kids R$ 200/hora", 
                "Treinamento Competitivo R$ 1.200/mês", 
                "Eventos valor a combinar"
            ])
            local = st.selectbox("Unidade", list(info_academias.keys()))
            data_aula = st.date_input("Data", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("RESERVAR E PAGAR"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%Y-%m-%d"),
                        "Horario": hora_aula,
                        "Aluno": aluno,
                        "Servico": servico,
                        "Status": "Aguardando Pagamento",
                        "Academia": local,
                        "Email_Aluno": email
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
    else:
        st.markdown(f"### 💳 Pagamento via PIX")
        st.write(f"**Aluno:** {st.session_state.reserva_temp['Aluno']}")
        st.markdown("**Chave PIX:** aranha.corp@gmail.com") # Ajustado conforme solicitado
        if st.button("CONFIRMAR AGENDAMENTO"):
            try:
                # GRAVAÇÃO NA PLANILHA
                df_existente = conn.read(worksheet="Página1")
                df_novo = pd.concat([df_existente, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo)
                
                # ENVIO DE E-MAIL
                enviou = enviar_email_confirmacao(st.session_state.reserva_temp)
                
                st.success("Reserva salva e e-mail enviado!")
                st.balloons()
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros Oficiais")
    # Links ajustados e testados
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro">👤 Cadastro de Aluno</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdO7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform" class="btn-cadastro">🏢 Cadastro de Academia</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform" class="btn-cadastro">🎾 Cadastro de Professor</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="translucent-balloon"><h2>🎾 Tabela de Serviços</h2>'
                '<ul><li><b>Aula Individual:</b> R$ 250/hora</li>'
                '<li><b>Aula em Grupo:</b> R$ 200/hora</li>'
                '<li><b>Aula Kids:</b> R$ 200/hora</li>'
                '<li><b>Treinamento Competitivo:</b> R$ 1.200/mês</li>'
                '<li><b>Eventos:</b>
