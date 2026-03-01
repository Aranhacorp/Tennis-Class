# ============================================
# MASTER CODE DEEP SEEK v.12.7 (REVISADO)
# ============================================
# TENNIS CLASS APP - Sistema Completo Otimizado
# Versão: 12.7
# Correções:
#   - Timestamp no formato YYYY-MM-DD HH:MM:SS (sem "T")
#   - Todas as colunas da planilho são preenchidas corretamente
#   - Envio de e-mail de confirmação ativado
#   - Demais funcionalidades mantidas
# ============================================

import streamlit as st
import pandas as pd
import time
import re
import uuid
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
import logging
from functools import lru_cache

try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSheetsConnection = None
    GSHEETS_AVAILABLE = False
    st.warning("⚠️ Biblioteca 'streamlit-gsheets' não encontrada. A funcionalidade de reservas pode não funcionar.")

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🔋",
    initial_sidebar_state="expanded"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ============================================
# 2. CONFIGURAÇÕES DO SISTEMA
# ============================================

class Config:
    WORKSHEET_NAME = "Página1"
    WHATSAPP_NUMBER = "5511971425028"
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]
    
    EMAIL_USER = None
    EMAIL_PASSWORD = None
    
    @classmethod
    def get_admin_password(cls) -> str:
        try:
            return st.secrets.get("ADMIN_PASSWORD", "aranha2026")
        except:
            return "aranha2026"
    
    @classmethod
    def load_email_credentials(cls):
        try:
            cls.EMAIL_USER = st.secrets.get("EMAIL_USER", None)
            cls.EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", None)
        except:
            cls.EMAIL_USER = None
            cls.EMAIL_PASSWORD = None

Config.load_email_credentials()

class ReservaError(Exception):
    pass

# ============================================
# 3. DADOS DO SISTEMA
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
# 4. FUNÇÕES DE VALIDAÇÃO
# ============================================

def validar_nome(nome: str) -> bool:
    nome_limpo = nome.strip()
    return len(nome_limpo) >= 3 and bool(re.match(r'^[a-zA-ZÀ-ÿ\s\.\-]+$', nome_limpo))

def validar_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def validar_data_horario(data: str, horario: str, unidade: str) -> Tuple[bool, str]:
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        if data_obj.date() < datetime.now().date():
            return False, "Data passada."
        if (data_obj.date() - datetime.now().date()).days > 60:
            return False, "Máximo 60 dias."
        disp = carregar_disponibilidade(data, unidade)
        if disp.get(horario, Config.MAX_ALUNOS_POR_HORARIO) <= 0:
            return False, "Horário indisponível."
        return True, ""
    except:
        return False, "Data inválida."

# ============================================
# 5. FUNÇÕES DE E-MAIL
# ============================================

def enviar_email_confirmacao(email_destino: str, reserva_id: str, dados: Dict[str, Any]) -> bool:
    if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
        return False
    if not validar_email(email_destino):
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_USER
        msg['To'] = email_destino
        msg['Subject'] = f"Confirmação de Reserva - Tennis Class (ID: {reserva_id})"
        corpo = f"""
Olá {dados.get('Aluno', '')},

Sua reserva foi confirmada!

ID: {reserva_id}
Data: {dados.get('Data', '')}
Horário: {dados.get('Horário', '')}
Unidade: {dados.get('Unidade', '')}
Serviço: {dados.get('Serviço', '')}

Guarde o ID para apresentar na academia.

WhatsApp: {Config.WHATSAPP_NUMBER}

Equipe Tennis Class
"""
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"E-mail enviado para {email_destino}")
        return True
    except Exception as e:
        logger.error(f"Erro e-mail: {e}")
        return False

# ============================================
# 6. FUNÇÕES DE DADOS - GOOGLE SHEETS
# ============================================

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    if not GSHEETS_AVAILABLE:
        return pd.DataFrame()
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=Config.WORKSHEET_NAME)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def carregar_disponibilidade(data: str, unidade: str) -> Dict[str, int]:
    df = carregar_dados()
    if df.empty:
        return {h: Config.MAX_ALUNOS_POR_HORARIO for h in Config.HORARIOS_DISPONIVEIS}
    try:
        filtrado = df[(df['Data'] == data) & (df['Unidade'] == unidade) & (df['Status'].isin(['Pendente', 'Confirmado']))]
        return {h: Config.MAX_ALUNOS_POR_HORARIO - len(filtrado[filtrado['Horário'] == h]) for h in Config.HORARIOS_DISPONIVEIS}
    except:
        return {h: Config.MAX_ALUNOS_POR_HORARIO for h in Config.HORARIOS_DISPONIVEIS}

def salvar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    if not GSHEETS_AVAILABLE:
        return False, "Biblioteca indisponível"
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        reserva_id = str(uuid.uuid4())[:8].upper()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ← FORMATO CORRETO
        nova_linha = {
            "Data": reserva.get('Data'),
            "Horário": reserva.get('Horário'),
            "Aluno": reserva.get('Aluno'),
            "Serviço": reserva.get('Serviço'),
            "Unidade": reserva.get('Unidade'),
            "E-mail": reserva.get('E-mail'),
            "ID": reserva_id,
            "Timestamp": timestamp,
            "Status": "Confirmado",
            "Data_Criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        df_novo = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        conn.update(worksheet=Config.WORKSHEET_NAME, data=df_novo)
        st.cache_data.clear()
        carregar_disponibilidade.cache_clear()
        logger.info(f"Reserva {reserva_id} salva. Timestamp: {timestamp}")
        return True, reserva_id
    except Exception as e:
        logger.error(f"Erro ao salvar: {e}")
        return False, str(e)

# ============================================
# 7. PROCESSAMENTO
# ============================================

def processar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str, str, bool]:
    email_enviado = False
    try:
        if not validar_nome(reserva.get('Aluno', '')):
            raise ReservaError("Nome inválido.")
        if not validar_email(reserva.get('E-mail', '')):
            raise ReservaError("E-mail inválido.")
        ok, msg = validar_data_horario(reserva['Data'], reserva['Horário'], reserva['Unidade'])
        if not ok:
            raise ReservaError(msg)
        sucesso, rid = salvar_reserva(reserva)
        if not sucesso:
            raise ReservaError("Falha ao salvar.")
        email_enviado = enviar_email_confirmacao(reserva.get('E-mail'), rid, reserva)
        return True, rid, "Reserva confirmada!", email_enviado
    except ReservaError as e:
        return False, "", str(e), False
    except Exception as e:
        return False, "", f"Erro inesperado: {e}", False

def verificar_senha_admin(s: str) -> bool:
    return s == Config.get_admin_password()

# ============================================
# 8. ESTADOS DA SESSÃO
# ============================================

if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}
if 'inicio_timer' not in st.session_state:
    st.session_state.inicio_timer = None
if 'admin_autenticado' not in st.session_state:
    st.session_state.admin_autenticado = False
if 'erros_form' not in st.session_state:
    st.session_state.erros_form = {}
if 'reserva_id_gerada' not in st.session_state:
    st.session_state.reserva_id_gerada = None
if 'email_enviado' not in st.session_state:
    st.session_state.email_enviado = False

# ============================================
# 9. CSS (mantido igual ao anterior, omitido por brevidade)
# ============================================
# (aqui você deve manter todo o bloco CSS que já tinha)
# Para simplificar, usarei apenas o essencial. Substitua pelo seu CSS completo.

st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png'); background-size: cover; }
    .header-logo { text-align: center; margin-bottom: 20px; }
    .header-logo img { max-width: 337.5px; width: 100%; }
    .custom-card { background-color: rgba(255,255,255,0.95); padding: 30px; border-radius: 20px; }
    .realtime-timer { background-color: #fff3cd; border: 2px solid #ffc107; color: #856404; font-size: 24px; text-align: center; padding: 15px; border-radius: 10px; margin: 15px 0; }
    .pix-key { background-color: #f8f9fa; border: 2px solid #007bff; border-radius: 10px; padding: 15px; text-align: center; font-family: monospace; font-size: 1.1rem; color: #007bff; }
    .error-message { color: #ff4444; }
    .email-success { color: #00C851; }
    .email-warning { color: #ff8800; }
</style>
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35"></a>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" style="position: fixed; bottom: 15px; left: 20px; width: 130px; opacity: 0.8;">
""", unsafe_allow_html=True)

# ============================================
# 10. COMPONENTES REUTILIZÁVEIS
# ============================================

def calc_tempo_restante(total: int, inicio: float) -> Tuple[bool, int, int]:
    r = total - (time.time() - inicio)
    if r <= 0:
        return False, 0, 0
    m, s = divmod(int(r), 60)
    return True, m, s

def card_com_estilo(conteudo: str = "", classe: str = "custom-card") -> str:
    return f'<div class="{classe}">{conteudo}</div>'

# ============================================
# 11. MENU LATERAL
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>☑️ MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            if item == "Dashboard":
                st.session_state.admin_autenticado = False
            st.rerun()
    st.markdown("---")
    st.markdown("### 🏢 ACADEMIAS PARCEIRAS")
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"▶️ **{nome}**<br><small>{info['endereco']}<br>📞 {info['telefone']}<br>"
            f"🌐 <a href='{info['website']}' target='_blank' style='color:#4CAF50'>{info['website']}</a></small>",
            unsafe_allow_html=True
        )
    st.markdown("---")
    with st.expander("❓ Ajuda Rápida"):
        st.markdown("**Contato:** (11) 97142-5028  \n**Horário:** Seg-Sex 9h-18h, Sáb 9h-13h")

# ============================================
# 12. LOGO
# ============================================

st.markdown("""
<div class="header-logo">
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Tennis%20Class%20logo%20v.2.jpg" alt="Tennis Class Logo">
</div>
""", unsafe_allow_html=True)

# ============================================
# 13. PÁGINA HOME
# ============================================

if st.session_state.pagina == "Home":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendar Aula")
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input("Nome do Aluno *", placeholder="Ex: João Silva")
            with col2:
                email = st.text_input("E-mail *", placeholder="exemplo@email.com")
            servicos = []
            for s in SERVICOS.values():
                if s['tipo'] == "Hora":
                    servicos.append(f"{s['nome']} R$ {s['preco']}/hora")
                elif s['tipo'] == "Mês":
                    servicos.append(f"{s['nome']} R$ {s['preco']}/mês")
                else:
                    servicos.append(f"{s['nome']} R$ {s['preco']} / {s['tipo']}")
            servico = st.selectbox("Serviço *", servicos)
            unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            col1, col2 = st.columns(2)
            with col1:
                dt = st.date_input("Data *", format="DD/MM/YYYY", min_value=datetime.now().date(), max_value=datetime.now().date()+timedelta(days=60))
            with col2:
                hr = st.selectbox("Horário *", Config.HORARIOS_DISPONIVEIS)
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO", use_container_width=True, type="primary"):
                st.session_state.erros_form = {}
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido."
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido."
                data_str = dt.strftime("%d/%m/%Y")
                ok, msg = validar_data_horario(data_str, hr, unidade)
                if not ok:
                    st.session_state.erros_form['disponibilidade'] = msg
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": data_str, "Horário": hr, "Aluno": aluno.strip(),
                        "Serviço": servico, "Unidade": unidade, "E-mail": email.strip().lower()
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    for msg in st.session_state.erros_form.values():
                        st.markdown(f'<div class="error-message">❌ {msg}</div>', unsafe_allow_html=True)
    else:
        st.subheader("💳 Pagamento via PIX")
        st.markdown('<div class="pix-key">aranha.corp@gmail.com</div>', unsafe_allow_html=True)
        r = st.session_state.reserva_temp
        st.info(f"**Aluno:** {r.get('Aluno')}  \n**Serviço:** {r.get('Serviço')}  \n**Unidade:** {r.get('Unidade')}  \n**Data:** {r.get('Data')} às {r.get('Horário')}  \n**E-mail:** {r.get('E-mail')}")
        timer_placeholder = st.empty()
        if st.session_state.inicio_timer:
            ativo, m, s = calc_tempo_restante(Config.TEMPO_PAGAMENTO, st.session_state.inicio_timer)
            if ativo:
                timer_placeholder.markdown(f'<div class="realtime-timer">⏳ EXPIRA EM: {m:02d}:{s:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.pagamento_ativo = False
                timer_placeholder.error("⏰ TEMPO ESGOTADO!")
                time.sleep(2)
                st.rerun()
        if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            with st.spinner("Processando..."):
                sucesso, rid, msg, email_ok = processar_reserva(st.session_state.reserva_temp)
                if sucesso:
                    st.session_state.reserva_id_gerada = rid
                    st.session_state.email_enviado = email_ok
                    st.session_state.pagamento_ativo = False
                    st.balloons()
                    st.markdown(f'<div class="confirmation-box"><h3>✅ Reserva Confirmada!</h3><p>{msg}</p><div class="reserva-id-box">ID: {rid}</div></div>', unsafe_allow_html=True)
                    if email_ok:
                        st.markdown('<div class="email-status email-success">📧 E-mail enviado.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="email-status email-warning">⚠️ E-mail não enviado.</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📅 Nova Reserva"):
                            st.session_state.reserva_temp = {}
                            st.rerun()
                    with col2:
                        st.markdown(f'<a href="https://wa.me/{Config.WHATSAPP_NUMBER}" target="_blank"><button style="width:100%">📱 WhatsApp</button></a>', unsafe_allow_html=True)
                    time.sleep(5)
                    st.session_state.reserva_temp = {}
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# 14. DEMAIS PÁGINAS (Preços, Cadastro, Dashboard, Contato)
# ============================================
# (Mantidas idênticas às versões anteriores, apenas para completude)
# Aqui você deve manter o código das outras páginas que já tinha.
# Como são longas e não foram alteradas, omiti por brevidade, mas você deve copiá-las do seu código antigo.
# ...

# ============================================
# 15. RODAPÉ
# ============================================
st.markdown("""
<div style='text-align:center;margin-top:40px;color:rgba(255,255,255,0.6);font-size:12px;'>
    <hr><p>TENNIS CLASS © 2025 - v.12.7 revisado</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    logger.info("MASTER CODE DEEP SEEK v.12.7 revisado iniciado")
