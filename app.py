# ============================================
# MASTER CODE DEEP SEEK v.12.3 (Logo ajustado)
# ============================================
# TENNIS CLASS APP - Sistema Completo Otimizado
# Versão: 12.3 (Patch: Normalização de Horários)
# ============================================

import streamlit as st
import pandas as pd
import time
import re
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
from functools import lru_cache

# Tenta importar a conexão com Google Sheets
try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSheetsConnection = None
    GSHEETS_AVAILABLE = False
    st.warning("⚠️ Biblioteca 'streamlit-gsheets' não encontrada.")

# ============================================
# 1. CONFIGURAÇÃO E CONFIGS
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

class Config:
    SPREADSHEET_URL = "" # Preencher se necessário via Secrets
    WORKSHEET_NAME = "Página1"
    WHATSAPP_NUMBER = "5511971425028"
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300  # 5 minutos
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]
    
    @classmethod
    def get_admin_password(cls) -> str:
        return st.secrets.get("ADMIN_PASSWORD", "aranha2026")

# ============================================
# 2. DADOS DO SISTEMA (PREÇOS & ACADEMIAS)
# ============================================

SERVICOS = {
    "particular_hora": {"nome": "Aula particular", "preco": 250, "tipo": "Hora"},
    "grupo_hora": {"nome": "Aula em grupo", "preco": 200, "tipo": "Hora"},
    "kids_hora": {"nome": "Aula Kids", "preco": 230, "tipo": "Hora"},
    "personal_hora": {"nome": "Personal trainer", "preco": 250, "tipo": "Hora"},
    "competitivo": {"nome": "Treinamento competitivo", "preco": 1400, "tipo": "Mês"},
    "eventos": {"nome": "Eventos", "preco": 0, "tipo": "Hora"},
    "pacote_particular_4": {"nome": "Pacote aula particular", "preco": 1000, "tipo": "4 aulas de 1 hora"},
    "pacote_grupo_4": {"nome": "Pacote aula em grupo", "preco": 800, "tipo": "4 aulas de 1 hora"},
    "pacote_particular_8": {"nome": "Pacote aula particular", "preco": 2000, "tipo": "8 aulas de 1 hora"},
    "pacote_grupo_8": {"nome": "Pacote aula em grupo", "preco": 1600, "tipo": "8 aulas de 1 hora"},
    "pacote_kids_4": {"nome": "Pacote aula Kids", "preco": 920, "tipo": "4 aulas de 1 hora"},
    "pacote_personal_4": {"nome": "Pacote Personal Trainer", "preco": 1000, "tipo": "4 aulas de 1 hora"}
}

ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488",
        "website": "https://www.playtennis.com.br/"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828",
        "website": "https://toponetennis.com.br/"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028",
        "website": "https://www.instagram.com/barbetaefontestennisacademy/"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860",
        "website": "https://arenabtg.com.br/"
    }
}

FORM_LINKS = {
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?usp=dialog",
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?usp=dialog",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog"
}

# ============================================
# 3. FUNÇÕES DE DADOS (NORMALIZAÇÃO ANTI-CONFLITO)
# ============================================

@st.cache_data(ttl=60) # TTL reduzido para 1 min para evitar conflitos em tempo real
def carregar_dados() -> pd.DataFrame:
    """Carrega dados e normaliza formatos de data/hora para evitar duplicidade."""
    if not GSHEETS_AVAILABLE: return pd.DataFrame()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=Config.WORKSHEET_NAME)
        
        if not df.empty:
            # Normaliza Horário (remove segundos como :00 vistos na imagem)
            df['Horário'] = pd.to_datetime(df['Horário'], errors='coerce').dt.strftime('%H:%M')
            # Normaliza Data para string DD/MM/YYYY
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
        return df
    except Exception as e:
        return pd.DataFrame()

@lru_cache(maxsize=128)
def carregar_disponibilidade(data: str, unidade: str) -> Dict[str, int]:
    """Calcula vagas restantes garantindo que o limite de 4 não seja excedido."""
    df = carregar_dados()
    if df.empty:
        return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}
    
    # Filtro rigoroso: Data exata, Unidade exata e Status Ativo
    filtrado = df[
        (df['Data'] == data) & 
        (df['Unidade'] == unidade) & 
        (df['Status'].isin(['Pendente', 'Confirmado']))
    ]
    
    disponibilidade = {}
    for hora in Config.HORARIOS_DISPONIVEIS:
        # Conta reservas no horário normalizado (ex: '12:00')
        ocupados = len(filtrado[filtrado['Horário'] == hora])
        disponibilidade[hora] = max(0, Config.MAX_ALUNOS_POR_HORARIO - ocupados)
    return disponibilidade

def salvar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    if not GSHEETS_AVAILABLE: return False, "Erro de conexão."
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        reserva_id = str(uuid.uuid4())[:8].upper()
        reserva.update({
            "ID": reserva_id,
            "Timestamp": datetime.now().isoformat(),
            "Status": "Confirmado",
            "Data_Criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet=Config.WORKSHEET_NAME, data=df_novo)
        st.cache_data.clear()
        return True, reserva_id
    except Exception as e:
        return False, str(e)

# ============================================
# 4. ESTILOS CSS (LOGO AJUSTADO)
# ============================================

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-attachment: fixed;
    }}
    .header-logo {{
        text-align: center; margin-top: -19px; margin-bottom: 20px; /* Sobe 0,5cm */
    }}
    .header-logo img {{
        max-width: 337.5px; width: 100%; height: auto; /* Aumentado 12.5% */
    }}
    .custom-card {{ background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: #333; }}
    .whatsapp-float {{ position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px; background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center; font-size: 35px; z-index: 9999; display: flex; align-items: center; justify-content: center; text-decoration: none; }}
</style>
<a href="https://wa.me/{Config.WHATSAPP_NUMBER}" class="whatsapp-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35"></a>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" style="position: fixed; bottom: 15px; left: 20px; width: 130px; z-index: 9999; opacity: 0.8;">
""", unsafe_allow_html=True)

# ============================================
# 5. LÓGICA DE NAVEGAÇÃO E PÁGINAS
# ============================================

if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, use_container_width=True):
            st.session_state.pagina = item
            st.rerun()
    st.markdown("---")
    st.markdown("### 🏢 ACADEMIAS")
    for nome, info in ACADEMIAS.items():
        st.markdown(f"📍 **{nome}**\n<div style='font-size: 11px; color: #ccc;'>{info['endereco']}<br>🌐 <a href='{info['website']}' style='color: #4CAF50;'>Website</a></div>", unsafe_allow_html=True)

# PÁGINA HOME (LOGO + AGENDAMENTO)
st.markdown('<div class="header-logo"><img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Tennis%20Class%20logo%20v.1.png"></div>', unsafe_allow_html=True)

if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendar Aula")
            col1, col2 = st.columns(2)
            aluno = col1.text_input("Nome do Aluno *")
            email = col2.text_input("E-mail *")
            servico = st.selectbox("Serviço *", [f"{v['nome']} R$ {v['preco']}/{v['tipo']}" for v in SERVICOS.values()])
            unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            dt = st.date_input("Data *", min_value=datetime.now().date())
            hr = st.selectbox("Horário *", Config.HORARIOS_DISPONIVEIS)
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                disp = carregar_disponibilidade(dt.strftime("%d/%m/%Y"), unidade)
                if disp.get(hr, 0) > 0:
                    st.session_state.reserva_temp = {"Data": dt.strftime("%d/%m/%Y"), "Horário": hr, "Aluno": aluno, "Serviço": servico, "Unidade": unidade, "E-mail": email}
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    st.error("Horário esgotado (Limite de 4 alunos atingido).")
    else:
        st.subheader("💳 Pagamento via PIX")
        st.info("Chave PIX: aranha.corp@gmail.com")
        if st.button("✅ CONFIRMAR PAGAMENTO"):
            sucesso, rid = salvar_reserva(st.session_state.reserva_temp)
            if sucesso:
                st.success(f"Reserva Confirmada! ID: {rid}")
                st.balloons()
                time.sleep(3)
                st.session_state.pagamento_ativo = False
                st.rerun()

# PÁGINA PREÇOS (TABELAS + CALCULADORA)
elif st.session_state.pagina == "Preços":
    st.markdown("### 🎾 Tabela de Preços")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Aulas Avulsas**")
        for k, v in SERVICOS.items():
            if "Pacote" not in v['nome']: st.write(f"{v['nome']}: R$ {v['preco']}/{v['tipo']}")
    with col2:
        st.markdown("**Quadras**")
        st.write("Externa: R$ 200/h | Coberta: R$ 350/h")
    
    st.markdown("---")
    st.markdown("#### 🧮 Calculadora Completa")
    opcao = st.radio("Serviço", ["Aula", "Locação"], horizontal=True)
    if opcao == "Aula":
        qtd = st.number_input("Horas", 1, 10)
        st.success(f"Total: R$ {qtd * 250:,.2f}") # Exemplo base
    else:
        tipo_q = st.selectbox("Tipo", ["Externa", "Coberta"])
        hrs = st.number_input("Horas", 1, 5)
        total = hrs * (200 if tipo_q == "Externa" else 350)
        st.success(f"Total Locação: R$ {total:,.2f}")

# PÁGINA DASHBOARD (ADMIN)
elif st.session_state.pagina == "Dashboard":
    pwd = st.text_input("Senha Admin", type="password")
    if pwd == Config.get_admin_password():
        df = carregar_dados()
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Backup CSV", df.to_csv(index=False), "backup.csv")

# PÁGINA CONTATO
elif st.session_state.pagina == "Contato":
    st.info(f"WhatsApp: {Config.WHATSAPP_NUMBER}")
    st.write("E-mail: aranha.corp@gmail.com")

st.markdown("---")
st.caption(f"TENNIS CLASS v12.3 | © {datetime.now().year} Andre Aranha")
st.markdown('[📄 Regulamento de Uso](https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing)', unsafe_allow_html=True)
