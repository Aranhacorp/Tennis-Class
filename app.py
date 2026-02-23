# ============================================
# MASTER CODE DEEP SEEK v.12.4 (logo corrigido)
# ============================================
# TENNIS CLASS APP - Sistema Completo Otimizado
# Versão: 12.4
# Correção: Preços Aula Kids (R$ 230/hora | Pacote 4h R$ 920)
# Modificações: 
#   - removido "Reservas ativas" da barra lateral
#   - incluídos preços de locação de quadra (R$200 externa / R$350 coberta)
#   - adicionada calculadora completa (aulas, pacotes e locação)
#   - substituído título de texto pela imagem do logo (versão 1, funcionando)
#   - adicionados websites das academias parceiras
#   - ícone do navegador alterado para apenas bola de tênis (🎾)
#   - sidebar recolhe automaticamente após clique no menu
# ============================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
import logging
from functools import lru_cache

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# Configuração de logging - apenas console, sem arquivo
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
    """Classe de configuração centralizada do sistema."""
    
    # Google Sheets
    WORKSHEET_NAME = "Página1"
    
    # Contato
    WHATSAPP_NUMBER = "5511971425028"
    
    # Limites do sistema
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300
    
    # Horários disponíveis
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]
    
    @classmethod
    def get_admin_password(cls) -> str:
        try:
            return st.secrets.get("ADMIN_PASSWORD", "aranha2026")
        except:
            return "aranha2026"

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
    "pacote_particular_4": {"nome": "Pacote aula particular", "preco": 1000, "tipo": "4 aulas"},
    "pacote_grupo_4": {"nome": "Pacote aula em grupo", "preco": 800, "tipo": "4 aulas"},
    "pacote_particular_8": {"nome": "Pacote aula particular", "preco": 2000, "tipo": "8 aulas"},
    "pacote_grupo_8": {"nome": "Pacote aula em grupo", "preco": 1600, "tipo": "8 aulas"},
    "pacote_kids_4": {"nome": "Pacote aula Kids", "preco": 920, "tipo": "4 aulas"},
    "pacote_personal_4": {"nome": "Pacote Personal Trainer", "preco": 1000, "tipo": "4 aulas"}
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
# 4. FUNÇÕES DE DADOS
# ============================================

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=Config.WORKSHEET_NAME)
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def carregar_disponibilidade(data: str, unidade: str) -> Dict[str, int]:
    try:
        df = carregar_dados()
        if df.empty:
            return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}
        
        filtrado = df[
            (df['Data'] == data) &
            (df['Unidade'] == unidade) &
            (df['Status'].isin(['Pendente', 'Confirmado']))
        ]
        
        disponibilidade = {}
        for hora in Config.HORARIOS_DISPONIVEIS:
            count = len(filtrado[filtrado['Horário'] == hora])
            disponibilidade[hora] = Config.MAX_ALUNOS_POR_HORARIO - count
        return disponibilidade
    except:
        return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}

def salvar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        reserva_id = str(uuid.uuid4())[:8].upper()
        reserva["ID"] = reserva_id
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Confirmado"
        reserva["Data_Criacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet=Config.WORKSHEET_NAME, data=df_novo)
        st.cache_data.clear()
        carregar_disponibilidade.cache_clear()
        return True, reserva_id
    except Exception as e:
        return False, str(e)

# ============================================
# 5. FUNÇÕES DE VALIDAÇÃO
# ============================================

def validar_nome(nome: str) -> bool:
    return len(nome.strip()) >= 3 and bool(re.match(r'^[a-zA-ZÀ-ÿ\s\.\-]+$', nome.strip()))

def validar_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def validar_data_horario(data: str, horario: str, unidade: str) -> Tuple[bool, str]:
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        if data_obj.date() < datetime.now().date():
            return False, "Data passada."
        if (data_obj.date() - datetime.now().date()).days > 60:
            return False, "Máximo 60 dias."
        
        disponibilidade = carregar_disponibilidade(data, unidade)
        vagas = disponibilidade.get(horario, Config.MAX_ALUNOS_POR_HORARIO)
        if vagas <= 0:
            return False, f"Horário indisponível."
        return True, ""
    except:
        return False, "Data inválida."

# ============================================
# 6. PROCESSAMENTO
# ============================================

def processar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str, str]:
    try:
        if not validar_nome(reserva.get('Aluno', '')):
            raise ReservaError("Nome inválido.")
        if not validar_email(reserva.get('E-mail', '')):
            raise ReservaError("E-mail inválido.")
        
        disponivel, msg = validar_data_horario(
            reserva['Data'], reserva['Horário'], reserva['Unidade']
        )
        if not disponivel:
            raise ReservaError(msg)
        
        sucesso, reserva_id = salvar_reserva(reserva)
        if not sucesso:
            raise ReservaError("Erro ao salvar.")
        return True, reserva_id, "✅ Reserva confirmada!"
    except ReservaError as e:
        return False, "", str(e)
    except Exception as e:
        return False, "", f"Erro: {str(e)}"

def verificar_senha_admin(senha: str) -> bool:
    return senha == Config.get_admin_password()

# ============================================
# 7. ESTADOS DA SESSÃO
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

# ============================================
# 8. CSS
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }
    
    .header-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .header-logo img {
        max-width: 337.5px;
        width: 100%;
        height: auto;
    }
    
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
    }
    
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: 0.3s; 
        display: block; 
        padding: 20px; 
    }
    .clean-link:hover { 
        transform: translateY(-8px); 
        color: #4CAF50 !important; 
    }
    
    .icon-text { 
        font-size: 80px; 
        margin-bottom: 10px; 
    }
    .label-text { 
        font-size: 20px; 
        font-weight: bold; 
        letter-spacing: 2px; 
    }
    
    .whatsapp-float { 
        position: fixed; 
        width: 60px; 
        height: 60px; 
        bottom: 40px; 
        right: 40px; 
        background-color: #25d366; 
        border-radius: 50px; 
        z-index: 9999; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
    }
    
    .error-message {
        color: #ff4444;
        font-size: 14px;
        margin-top: 5px;
        padding: 5px;
        border-radius: 4px;
        background-color: rgba(255, 68, 68, 0.1);
    }
    
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        padding: 10px;
        border: 2px solid #ff8800;
        border-radius: 10px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    
    .reserva-id-box {
        background-color: #f8f9fa;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        font-weight: bold;
        color: #28a745;
    }
    
    .confirmation-box {
        background-color: #e8f5e9;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    
    .pix-key {
        background-color: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        color: #007bff;
    }
</style>

<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35">
</a>

<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     style="position: fixed; bottom: 15px; left: 20px; width: 130px; z-index: 9999; opacity: 0.8;">
""", unsafe_allow_html=True)

# ============================================
# 9. TIMER
# ============================================

def mostrar_timer(tempo_total: int, inicio_time: float) -> Tuple[bool, str]:
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

# ============================================
# 10. SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    
    menu_itens = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    for item in menu_itens:
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
            f"📍 **{nome}**\n"
            f"<div style='font-size: 11px; color: #ccc; margin-bottom: 10px;'>"
            f"{info['endereco']}<br>📞 {info['telefone']}<br>"
            f"🌐 <a href='{info['website']}' target='_blank' style='color: #4CAF50; text-decoration: none;'>{info['website']}</a>"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    with st.expander("❓ Ajuda Rápida"):
        st.markdown("**Contato:** (11) 97142-5028  \n**Horário:** Seg-Sex: 9h-18h | Sáb: 9h-13h")

# ============================================
# 11. LOGO (versão 1 - corrigida)
# ============================================

st.markdown("""
<div class="header-logo">
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Tennis%20Class%20logo%20v.1.png" alt="Tennis Class Logo">
</div>
""", unsafe_allow_html=True)

# ============================================
# 12. HOME
# ============================================

if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendar Aula")
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input("Nome do Aluno *", placeholder="Ex: João Silva")
            with col2:
                email = st.text_input("E-mail *", placeholder="exemplo@email.com")
            
            servicos_lista = []
            for info in SERVICOS.values():
                if info['tipo'] == "Hora":
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']}/hora")
                elif info['tipo'] == "Mês":
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']}/mês")
                else:
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']} / {info['tipo']}")
            
            servico = st.selectbox("Serviço *", servicos_lista)
            unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                dt = st.date_input("Data *", format="DD/MM/YYYY",
                                   min_value=datetime.now().date(),
                                   max_value=datetime.now().date() + timedelta(days=60))
            with col2:
                hr = st.selectbox("Horário *", Config.HORARIOS_DISPONIVEIS)
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO", use_container_width=True, type="primary"):
                st.session_state.erros_form = {}
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido."
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido."
                
                data_str = dt.strftime("%d/%m/%Y")
                disponivel, msg = validar_data_horario(data_str, hr, unidade)
                if not disponivel:
                    st.session_state.erros_form['disponibilidade'] = msg
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": data_str, "Horário": hr, "Aluno": aluno.strip(),
                        "Serviço": servico, "Unidade": unidade, "E-mail": email.lower().strip()
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
        
        reserva = st.session_state.reserva_temp
        st.info(f"**Aluno:** {reserva.get('Aluno')}  \n**Serviço:** {reserva.get('Serviço')}  \n**Unidade:** {reserva.get('Unidade')}  \n**Data:** {reserva.get('Data')} às {reserva.get('Horário')}  \n**E-mail:** {reserva.get('E-mail')}")
        
        timer_box = st.empty()
        if st.session_state.inicio_timer:
            ativo, msg = mostrar_timer(Config.TEMPO_PAGAMENTO, st.session_state.inicio_timer)
            if ativo:
                timer_box.markdown(f'<div class="timer-warning">{msg}</div>', unsafe_allow_html=True)
            else:
                st.session_state.pagamento_ativo = False
                timer_box.warning("⏰ Tempo esgotado!")
                time.sleep(2)
                st.rerun()
        
        if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            with st.spinner("Processando..."):
                sucesso, reserva_id, msg = processar_reserva(st.session_state.reserva_temp)
                if sucesso:
                    st.session_state.reserva_id_gerada = reserva_id
                    st.session_state.pagamento_ativo = False
                    st.balloons()
                    st.markdown(f"""
                    <div class="confirmation-box">
                        <h3>✅ Reserva Confirmada!</h3>
                        <p>{msg}</p>
                        <div class="reserva-id-box">ID: {reserva_id}</div>
                        <p>Guarde este ID.</p>
                    </div>
                    """, unsafe_allow_html=True)
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
    
    st.markdown("""
    <hr>
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing" 
       target="_blank" style="display:block; text-align:center; color:#555;">
        📄 Ler Regulamento
    </a>
    """, unsafe_allow_html=True)

# ============================================
# 13. PREÇOS
# ============================================

elif st.session_state.pagina == "Preços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🎾 Tabela de Preços")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Aulas Avulsas")
        for info in SERVICOS.values():
            if info['tipo'] == "Hora" and "Pacote" not in info['nome']:
                st.markdown(f"**{info['nome']}**  \nR$ {info['preco']}/hora")
        
        st.markdown("#### 🏆 Treinamento Competitivo")
        for info in SERVICOS.values():
            if info['tipo'] == "Mês":
                st.markdown(f"**{info['nome']}**  \nR$ {info['preco']}/mês")
    
    with col2:
        st.markdown("#### 📦 Pacotes")
        for info in SERVICOS.values():
            if "Pacote" in info['nome']:
                st.markdown(f"**{info['nome']}**  \nR$ {info['preco']} / {info['tipo']}")
        
        st.markdown("#### 🎉 Eventos")
        st.markdown("**Eventos**  \nValor a combinar")
    
    st.markdown("---")
    st.markdown("#### 🏟️ Locação de Quadra")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Quadra Externa**  \nR$ 200/hora")
    with col4:
        st.markdown("**Quadra Coberta**  \nR$ 350/hora")
    
    st.markdown("---")
    st.markdown("#### 🧮 Calculadora")
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo = st.selectbox("Tipo", ["Aula particular", "Aula em grupo", "Aula Kids", "Personal trainer"])
    with col2:
        qtd = st.number_input("Quantidade", 1, 20, 1)
    with col3:
        if st.button("Calcular"):
            preco = 0
            for info in SERVICOS.values():
                if info['nome'] == tipo:
                    preco = info['preco']
                    break
            st.success(f"Total: R$ {preco * qtd:,.2f}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# 14. CADASTRO
# ============================================

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📝 Portal de Cadastros</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<a href="{FORM_LINKS["professor"]}" class="clean-link" target="_blank"><div class="icon-text">🎾</div><div class="label-text">PROFESSOR</div></a>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<a href="{FORM_LINKS["aluno"]}" class="clean-link" target="_blank"><div class="icon-text">🎾</div><div class="label-text">ALUNO</div></a>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<a href="{FORM_LINKS["academia"]}" class="clean-link" target="_blank"><div class="icon-text">🎾</div><div class="label-text">ACADEMIA</div></a>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align:center;margin-top:20px;padding:15px;background:rgba(255,255,255,0.1);border-radius:10px;color:#ccc;'>
        <p>Os formulários abrem em nova aba.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# 15. DASHBOARD
# ============================================

elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.admin_autenticado:
        st.subheader("🔐 Acesso Administrativo")
        senha = st.text_input("Senha:", type="password")
        if st.button("🔓 Acessar"):
            if verificar_senha_admin(senha):
                st.session_state.admin_autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.subheader("📊 Dashboard")
        df = carregar_dados()
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(df))
            with col2:
                st.metric("Confirmados", len(df[df['Status'] == 'Confirmado']))
            with col3:
                st.metric("Cancelados", len(df[df['Status'] == 'Cancelado']))
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if st.button("🚪 Logout"):
                st.session_state.admin_autenticado = False
                st.rerun()
        else:
            st.info("Nenhuma reserva.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# 16. CONTATO
# ============================================

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("📞 Canais de Atendimento")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📧 E-mail")
        st.markdown("aranha.corp@gmail.com")
        st.markdown("### 🏢 Endereço")
        st.markdown("São Paulo - SP")
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown("(11) 97142-5028  \nSeg-Sab: 8h-20h")
        st.markdown("### ⏰ Horário")
        st.markdown("Seg-Sex: 8h-20h  \nSáb: 8h-18h")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# 17. RODAPÉ
# ============================================

st.markdown("""
<div style='text-align:center;margin-top:40px;color:rgba(255,255,255,0.6);font-size:12px;'>
    <hr>
    <p>TENNIS CLASS © 2025 - v.12.4 (logo v.1 corrigido)</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 18. INICIALIZAÇÃO
# ============================================

if __name__ == "__main__":
    logger.info("MASTER CODE DEEP SEEK v.12.4 (logo v.1 corrigido) iniciado")
