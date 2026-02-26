# ============================================
# MASTER CODE DEEP SEEK v.12.6
# ============================================
# TENNIS CLASS - Sistema Completo
# Calendário Visual Inteligente
# Google Sheets + Menu + Validação + Estrutura Profissional
# ============================================


# ============================================
# 1. IMPORTAÇÕES
# ============================================

import streamlit as st
import pandas as pd
import re
import uuid
import logging
from datetime import datetime, timedelta
from functools import lru_cache


# ============================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS",
    layout="wide",
    page_icon="🎾"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# 3. CONFIGURAÇÕES GERAIS
# ============================================

class Config:
    WORKSHEET_NAME = "Página1"
    MAX_ALUNOS_POR_HORARIO = 4
    HORARIOS = [f"{h:02d}:00" for h in range(7, 23)]
    LIMITE_DIAS = 60


# ============================================
# 4. DADOS DO NEGÓCIO
# ============================================

SERVICOS = {
    "Aula Particular": 250,
    "Aula em Grupo": 200,
    "Aula Kids": 230,
    "Personal Trainer": 250,
    "Treinamento Competitivo (Mensal)": 1400,
}

ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": "R. Estado de Israel, 860 - SP",
    "TOP One Tennis": "Av. Indianópolis, 647 - SP",
    "MELL Tennis": "Rua Oscar Gomes Cardim, 535 - SP",
    "ARENA BTG Morumbi": "Av. Maj. Sylvio de Magalhães Padilha - SP",
}


# ============================================
# 5. GOOGLE SHEETS
# ============================================

try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS = True
except:
    GSHEETS = False


@st.cache_data(ttl=300)
def carregar_dados():
    if not GSHEETS:
        return pd.DataFrame()
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=Config.WORKSHEET_NAME)


@lru_cache(maxsize=128)
def disponibilidade(data: str, unidade: str):
    df = carregar_dados()

    if df.empty:
        return {h: Config.MAX_ALUNOS_POR_HORARIO for h in Config.HORARIOS}

    filtrado = df[(df["Data"] == data) & (df["Unidade"] == unidade)]

    mapa = {}
    for h in Config.HORARIOS:
        ocupados = len(filtrado[filtrado["Horário"] == h])
        mapa[h] = Config.MAX_ALUNOS_POR_HORARIO - ocupados

    return mapa


def salvar_reserva(reserva):
    if not GSHEETS:
        return False, "Google Sheets não configurado."

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = carregar_dados()

    reserva["ID"] = str(uuid.uuid4())[:8].upper()
    reserva["Timestamp"] = datetime.now().isoformat()
    reserva["Status"] = "Confirmado"

    df_final = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
    conn.update(worksheet=Config.WORKSHEET_NAME, data=df_final)

    st.cache_data.clear()
    return True, reserva["ID"]


# ============================================
# 6. VALIDAÇÕES
# ============================================

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def validar_campos(nome, email):
    if not nome.strip():
        return False, "Nome é obrigatório."
    if not validar_email(email):
        return False, "Email inválido."
    return True, ""


# ============================================
# 7. ESTADO DA SESSÃO
# ============================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "Home"

if "horario" not in st.session_state:
    st.session_state.horario = None


# ============================================
# 8. MENU LATERAL
# ============================================

with st.sidebar:
    st.title("MENU")

    if st.button("🏠 Home"):
        st.session_state.pagina = "Home"

    if st.button("💰 Preços"):
        st.session_state.pagina = "Preços"

    if st.button("📞 Contato"):
        st.session_state.pagina = "Contato"

    st.markdown("---")
    st.markdown("### 🏟 Academias")
    for nome, endereco in ACADEMIAS.items():
        st.markdown(f"**{nome}**")
        st.caption(endereco)


# ============================================
# 9. PÁGINA PREÇOS
# ============================================

if st.session_state.pagina == "Preços":

    st.title("💰 Tabela de Preços")

    for nome, preco in SERVICOS.items():
        st.markdown(f"**{nome}** — R$ {preco}")


# ============================================
# 10. PÁGINA CONTATO
# ============================================

elif st.session_state.pagina == "Contato":

    st.title("📞 Contato")
    st.write("WhatsApp: (11) 97142-5028")


# ============================================
# 11. PÁGINA HOME
# ============================================

elif st.session_state.pagina == "Home":

    st.title("🎾 TENNIS CLASS")
    st.subheader("📅 Agendar Aula")

    with st.form("form_agendamento"):

        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome do Aluno *")

        with col2:
            email = st.text_input("E-mail *")

        unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))

        data = st.date_input(
            "Data *",
            min_value=datetime.now().date(),
            max_value=(datetime.now() + timedelta(days=Config.LIMITE_DIAS)).date()
        )

        data_str = data.strftime("%d/%m/%Y")

        st.markdown("### ⏰ Horários Disponíveis")

        mapa = disponibilidade(data_str, unidade)
        colunas = st.columns(4)

        for i, h in enumerate(Config.HORARIOS):
            vagas = mapa.get(h, 0)
            with colunas[i % 4]:
                if vagas > 0:
                    if st.form_submit_button(f"🟢 {h}\n{vagas} vaga(s)"):
                        st.session_state.horario = h
                else:
                    st.markdown(
                        f"<div style='background:#ff4d4d;padding:8px;border-radius:6px;text-align:center;color:white;'>"
                        f"{h}<br>Lotado</div>",
                        unsafe_allow_html=True
                    )

        servico = st.selectbox("Serviço *", list(SERVICOS.keys()))

        confirmar = st.form_submit_button("✅ Confirmar")

        if confirmar:

            valido, msg = validar_campos(nome, email)

            if not valido:
                st.error(msg)

            elif not st.session_state.horario:
                st.error("Selecione um horário.")

            else:
                reserva = {
                    "Aluno": nome,
                    "E-mail": email,
                    "Data": data_str,
                    "Horário": st.session_state.horario,
                    "Serviço": servico,
                    "Unidade": unidade,
                }

                ok, resposta = salvar_reserva(reserva)

                if ok:
                    st.success("Agendamento realizado com sucesso!")
                    st.markdown(f"### 🎫 ID: `{resposta}`")
                    st.session_state.horario = None
                else:
                    st.error(resposta)


# ============================================
# 17. INICIALIZAÇÃO
# ============================================

if __name__ == "__main__":
    logger.info("Sistema TENNIS CLASS iniciado com sucesso.")
