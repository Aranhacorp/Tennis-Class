# ============================================
# TENNIS CLASS MANAGEMENT SYSTEM
# Versão 2.0 - Otimizado para Streamlit Cloud
# ============================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import os
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

# Configurar logging simplificado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tennis_class')

# Configuração da página Streamlit
st.set_page_config(
    page_title="TENNIS CLASS PRO",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# ============================================
# 2. CONSTANTES E CONFIGURAÇÕES
# ============================================

# Senha admin - usando secrets do Streamlit
try:
    SENHA_ADMIN = st.secrets.get("ADMIN_PASSWORD", "tennispro2024")
except:
    SENHA_ADMIN = "tennispro2024"

# Serviços disponíveis
SERVICOS = {
    "particular": {
        "nome": "Aula particular", 
        "preco": 250, 
        "icone": "🎾",
        "descricao": "Aula individual com foco total no aluno"
    },
    "grupo": {
        "nome": "Aula em grupo", 
        "preco": 200, 
        "icone": "👥",
        "descricao": "Aula em grupo de até 4 pessoas"
    },
    "kids": {
        "nome": "Aula Kids", 
        "preco": 200, 
        "icone": "👶",
        "descricao": "Aula especializada para crianças"
    },
    "personal": {
        "nome": "Personal trainer", 
        "preco": 250, 
        "icone": "💪",
        "descricao": "Treinamento personalizado"
    },
    "competitivo": {
        "nome": "Treinamento competitivo", 
        "preco": 1400, 
        "icone": "🏆",
        "descricao": "Pacote mensal para competidores"
    },
    "eventos": {
        "nome": "Eventos", 
        "preco": 0, 
        "icone": "🎉",
        "descricao": "Organização de eventos especiais"
    }
}

# Academias parceiras
ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860"
    }
}

# Links dos formulários
FORM_LINKS = {
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform",
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform"
}

# Constantes de tempo
TEMPO_PAGAMENTO = 300  # 5 minutos em segundos

# ============================================
# 3. FUNÇÕES AUXILIARES (SEM DEPENDÊNCIAS EXTERNAS)
# ============================================

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_nome(nome: str) -> bool:
    """Valida nome (mínimo 3 caracteres)."""
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    return True

def validar_telefone(telefone: str) -> bool:
    """Valida formato de telefone brasileiro."""
    telefone_limpo = re.sub(r'\D', '', telefone)
    return len(telefone_limpo) in [10, 11]

def formatar_moeda(valor: float) -> str:
    """Formata valor em moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def validar_data(data_str: str) -> Tuple[bool, str]:
    """Valida data no formato DD/MM/YYYY."""
    try:
        data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
        if data_obj < date.today():
            return False, "Data não pode ser no passado"
        return True, "Data válida"
    except ValueError:
        return False, "Data inválida. Use formato DD/MM/YYYY"

def validar_horario(horario: str) -> Tuple[bool, str]:
    """Valida horário no formato HH:00."""
    try:
        hora = int(horario.split(':')[0])
        if hora < 7 or hora > 22:
            return False, "Horário deve ser entre 07:00 e 22:00"
        if horario not in [f"{h:02d}:00" for h in range(7, 23)]:
            return False, "Horário deve ser em ponto (ex: 08:00)"
        return True, "Horário válido"
    except:
        return False, "Horário inválido. Use formato HH:00"

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Página1")
        
        if not df.empty:
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            if 'Timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def salvar_reserva(reserva: Dict[str, Any]) -> bool:
    """Salva uma reserva no Google Sheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        
        # Adiciona ID único e timestamp
        reserva["ID"] = str(uuid.uuid4())[:8]
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Pendente"
        
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache
        st.cache_data.clear()
        
        logger.info(f"Reserva salva: {reserva.get('Aluno')}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        st.error(f"❌ Erro ao salvar reserva: {str(e)}")
        return False

def mostrar_timer(tempo_total: int, inicio_time: float) -> Tuple[bool, str]:
    """Calcula e formata o tempo restante."""
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

# ============================================
# 4. ESTADOS DA SESSÃO
# ============================================

# Inicializar estados da sessão
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

# ============================================
# 5. CSS SIMPLIFICADO (EVITANDO ERROS DE SINTAXE)
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        min-height: 100vh;
    }
    .header-title { 
        color: white; 
        font-size: 50px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
        text-shadow: 2px 2px 4px black; 
    }
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
        margin: 0 auto;
        max-width: 1000px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: all 0.3s ease; 
        display: block; 
        padding: 20px; 
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.3);
        margin: 10px 0;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .clean-link:hover { 
        transform: translateY(-5px); 
        color: #FFD700 !important; 
        background-color: rgba(0, 0, 0, 0.5);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border-color: #FFD700;
    }
    .icon-text { 
        font-size: 50px;
        margin-bottom: 10px; 
    }
    .label-text { 
        font-size: 18px; 
        font-weight: bold; 
        letter-spacing: 1px; 
        margin-bottom: 8px;
    }
    .whatsapp-float { 
        position: fixed; 
        width: 60px; 
        height: 60px; 
        bottom: 40px; 
        right: 40px; 
        background-color: #25d366; 
        color: #FFF; 
        border-radius: 50px; 
        text-align: center; 
        font-size: 35px; 
        box-shadow: 2px 2px 3px #999; 
        z-index: 9999; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-decoration: none; 
        transition: all 0.3s ease;
    }
    .whatsapp-float:hover {
        transform: scale(1.1);
    }
    .assinatura-footer { 
        position: fixed; 
        bottom: 15px; 
        left: 20px; 
        width: 130px; 
        z-index: 9999; 
        opacity: 0.8;
    }
    .sidebar-detalhe { 
        font-size: 11px; 
        color: #ccc; 
        margin-bottom: 10px; 
        line-height: 1.2; 
    }
    .error-message {
        color: #ff4444;
        font-size: 14px;
        margin-top: 5px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(255, 68, 68, 0.1);
        border-left: 4px solid #ff4444;
    }
    .success-message {
        color: #00C851;
        font-size: 14px;
        margin-top: 5px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(0, 200, 81, 0.1);
        border-left: 4px solid #00C851;
    }
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        padding: 12px;
        border: 2px solid #ff8800;
        border-radius: 10px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    .tennis-ball-yellow {
        color: #FFD700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
    }
    .stButton > button {
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
</style>

<!-- Botão WhatsApp -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="WhatsApp">
</a>

<!-- Assinatura -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura">
""", unsafe_allow_html=True)

# ============================================
# 6. MENU LATERAL
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: #FFD700; text-align: center;'>🎾 MENU</h2>", 
                unsafe_allow_html=True)
    
    menu_items = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    
    for item in menu_items:
        if st.button(f"🎾 {item}", key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: #FFD700;'>🎾 ACADEMIAS</h3>", 
                unsafe_allow_html=True)
    
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"📍 **{nome}**\n"
            f"<div class='sidebar-detalhe'>"
            f"{info['endereco']}<br>📞 {info['telefone']}"
            f"</div>", 
            unsafe_allow_html=True
        )

# ============================================
# 7. TÍTULO PRINCIPAL
# ============================================

st.markdown('<div class="header-title"><span class="tennis-ball-yellow">🎾</span> TENNIS CLASS PRO</div>', 
            unsafe_allow_html=True)

# ============================================
# 8. LÓGICA DAS PÁGINAS
# ============================================

# PÁGINA: HOME
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.markdown('<h3 style="text-align: center; color: #333;">🎾 Agendar Aula</h3>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input(
                    "Nome do Aluno *",
                    placeholder="Ex: João Silva",
                    help="Digite seu nome completo"
                )
            with col2:
                email = st.text_input(
                    "E-mail *",
                    placeholder="Ex: joao.silva@email.com",
                    help="Digite um e-mail válido"
                )
            
            # Lista de serviços
            servicos_lista = [
                f"{SERVICOS[key]['icone']} {SERVICOS[key]['nome']} - R$ {SERVICOS[key]['preco']}"
                f"{'/hora' if key != 'competitivo' else '/mês'}"
                for key in SERVICOS.keys()
            ]
            
            col3, col4 = st.columns(2)
            with col3:
                servico = st.selectbox("Serviço *", servicos_lista)
            with col4:
                unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            col5, col6 = st.columns(2)
            with col5:
                dt = st.date_input("Data *", format="DD/MM/YYYY")
            with col6:
                hr = st.selectbox("Horário *", [f"{h:02d}:00" for h in range(7, 23)])
            
            telefone = st.text_input(
                "Telefone (opcional)",
                placeholder="(11) 99999-9999"
            )
            
            observacoes = st.text_area(
                "Observações (opcional)",
                placeholder="Alguma observação especial..."
            )
            
            submit = st.form_submit_button(
                "🎾 AVANÇAR PARA PAGAMENTO", 
                use_container_width=True,
                type="primary"
            )
            
            if submit:
                st.session_state.erros_form = {}
                
                # Validação
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome deve ter pelo menos 3 caracteres."
                
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido."
                
                if telefone and not validar_telefone(telefone):
                    st.session_state.erros_form['telefone'] = "Telefone inválido."
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": dt.strftime("%d/%m/%Y"),
                        "Horário": hr,
                        "Aluno": aluno.strip(),
                        "Serviço": servico,
                        "Unidade": unidade,
                        "E-mail": email.lower().strip(),
                        "Telefone": telefone.strip() if telefone else "",
                        "Observações": observacoes.strip() if observacoes else ""
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', 
                                  unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # QR Code
            st.image(
                "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
                width=250
            )
            
            # Chave PIX
            st.markdown("""
            <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;">
                <p style="font-family: monospace; font-size: 18px; margin: 0;">
                    <strong>aranha.corp@gmail.com</strong>
                </p>
                <p style="font-size: 14px; color: #666; margin-top: 10px;">
                    Copie a chave PIX e faça o pagamento
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Timer
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(
                TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                st.markdown(
                    f'<div class="timer-warning">{mensagem_timer}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.session_state.pagamento_ativo = False
                st.error("⏰ Tempo esgotado! Por favor, inicie uma nova reserva.")
                time.sleep(2)
                st.rerun()
        
        # Botão de confirmação
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎾 CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
                if salvar_reserva(st.session_state.reserva_temp):
                    st.balloons()
                    st.markdown(
                        '<div class="success-message">'
                        '✅ Reserva confirmada! Você receberá um e-mail de confirmação.'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Limpa estado
                    st.session_state.pagamento_ativo = False
                    st.session_state.reserva_temp = {}
                    time.sleep(3)
                    st.rerun()
        
        # Botão para cancelar
        if st.button("❌ Cancelar Pagamento", type="secondary", use_container_width=True):
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    # Regulamento
    st.markdown("""
    <hr style="margin: 30px 0;">
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYrE8rKsLdajbPi3fniwXVsBqco/edit" 
       target="_blank" 
       style="display: block; text-align: center; text-decoration: none; color: #555; padding: 10px;">
        📄 Ler Regulamento de Uso
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: PREÇOS
elif st.session_state.pagina == "Preços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Tabela de Preços</h3>', 
               unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agrupar por categoria
    categorias = {}
    for key, info in SERVICOS.items():
        categoria = info.get('categoria', 'Outros')
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append((key, info))
    
    for categoria, servicos in categorias.items():
        st.markdown(f"### {categoria}")
        for key, info in servicos:
            if key == "eventos":
                st.markdown(f"<div style='margin: 10px 0; padding-left: 20px;'>"
                          f"<span style='color: #FFD700;'>🎉</span> "
                          f"<strong>{info['nome']}:</strong> "
                          f"<em>Valor a combinar</em><br>"
                          f"<small style='color: #666;'>{info['descricao']}</small>"
                          f"</div>")
            else:
                unidade = "/hora" if key != "competitivo" else "/mês"
                st.markdown(f"<div style='margin: 10px 0; padding-left: 20px;'>"
                          f"<span style='color: #FFD700;'>{info['icone']}</span> "
                          f"<strong>{info['nome']}:</strong> "
                          f"R$ {info['preco']} {unidade}<br>"
                          f"<small style='color: #666;'>{info['descricao']}</small>"
                          f"</div>")
        st.markdown("---")
    
    st.info("💡 *Valores sujeitos a alteração. Consulte condições especiais para pacotes.*")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Portal de Cadastros</h3>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px; color: #666;'>
        Clique em uma das opções abaixo para preencher o formulário correspondente
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Formulário para novos alunos
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Para academias parceiras
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">🎾</div>
            <div class="label-text">PROFESSOR</div>
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Para professores parceiros
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: DASHBOARD
elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.admin_autenticado:
        st.markdown('<h3 style="text-align: center; color: #333;">🎾 Acesso Administrativo</h3>', 
                   unsafe_allow_html=True)
        
        senha = st.text_input(
            "Digite a senha de administrador:", 
            type="password",
            placeholder="Digite a senha..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Acessar", use_container_width=True):
                if senha == SENHA_ADMIN:
                    st.session_state.admin_autenticado = True
                    st.success("✅ Acesso concedido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        with col2:
            if st.button("🔙 Voltar", use_container_width=True):
                st.session_state.pagina = "Home"
                st.rerun()
    
    else:
        st.markdown('<h3 style="text-align: center; color: #333;">🎾 Dashboard - Reservas</h3>', 
                   unsafe_allow_html=True)
        
        # Botão de logout
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()
        
        st.markdown("---")
        
        # Carregar dados
        try:
            df = carregar_dados()
            
            if not df.empty:
                # Métricas
                total = len(df)
                pendentes = len(df[df['Status'] == 'Pendente'])
                confirmados = len(df[df['Status'] == 'Confirmado'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total)
                with col2:
                    st.metric("Pendentes", pendentes)
                with col3:
                    st.metric("Confirmados", confirmados)
                
                st.markdown("---")
                
                # Tabela
                st.dataframe(
                    df.sort_values('Data', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Data": st.column_config.DateColumn(
                            "Data",
                            format="DD/MM/YYYY"
                        ),
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Pendente", "Confirmado", "Cancelado"]
                        )
                    }
                )
                
                # Ações
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.success("✅ Dados atualizados!")
                        time.sleep(1)
                        st.rerun()
                
                with col2:
                    if not df.empty:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Exportar CSV",
                            data=csv,
                            file_name=f"reservas_tennis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
            else:
                st.info("📭 Nenhuma reserva encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dashboard: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Canais de Atendimento</h3>', 
               unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 E-mail")
        st.markdown("""
        <div style='padding: 20px; background: #f5f5f5; border-radius: 10px;'>
            <p style="font-size: 18px; margin: 0 0 10px 0;">
                <strong>aranha.corp@gmail.com</strong>
            </p>
            <p style="font-size: 14px; color: #666; margin: 0;">
                Respondemos em até 24 horas úteis
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown("""
        <div style='padding: 20px; background: #f5f5f5; border-radius: 10px;'>
            <p style="font-size: 18px; margin: 0 0 10px 0;">
                <strong>(11) 97142-5028</strong>
            </p>
            <p style="font-size: 14px; color: #666; margin: 0;">
                Atendimento direto
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulário de contato
    st.markdown("### ✉️ Envie uma mensagem")
    
    with st.form("contato_form"):
        nome_contato = st.text_input("Seu nome")
        email_contato = st.text_input("Seu e-mail")
        mensagem = st.text_area("Mensagem", height=150)
        
        if st.form_submit_button("📤 Enviar Mensagem", type="primary"):
            if nome_contato and email_contato and mensagem:
                if validar_email(email_contato):
                    st.success("✅ Mensagem enviada! Entraremos em contato em breve.")
                else:
                    st.error("❌ E-mail inválido.")
            else:
                st.warning("⚠️ Preencha todos os campos obrigatórios.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 9. RODAPÉ
# ============================================

st.markdown("""
<div style="text-align: center; color: #888; margin-top: 50px; padding: 20px; font-size: 12px;">
    <hr style="border: none; border-top: 1px solid #444; margin: 20px auto; width: 50%;">
    <p>Tennis Class Pro &copy; 2024 - Sistema de Gestão de Aulas de Tênis</p>
    <p style="font-size: 11px;">v2.0 - Desenvolvido com Streamlit</p>
</div>
""", unsafe_allow_html=True)
