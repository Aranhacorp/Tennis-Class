import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
from datetime import datetime
from typing import Dict, Any

# ============================================
# 1. CONFIGURAÇÃO E CONSTANTES
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# Constantes organizadas
SERVICOS = {
    "particular": {"nome": "Aula particular", "preco": 250, "icone": "🎾"},
    "grupo": {"nome": "Aula em grupo", "preco": 200, "icone": "🎾"},
    "kids": {"nome": "Aula Kids", "preco": 200, "icone": "🎾"},
    "personal": {"nome": "Personal trainer", "preco": 250, "icone": "🎾"},
    "competitivo": {"nome": "Treinamento competitivo", "preco": 1400, "icone": "🎾"},
    "eventos": {"nome": "Eventos", "preco": 0, "icone": "🎾"}
}

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

# LINKS CORRIGIDOS DOS FORMULÁRIOS - TESTADOS E FUNCIONAIS
FORM_LINKS = {
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform",
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform"
}

TEMPO_PAGAMENTO = 300  # 5 minutos em segundos

# ============================================
# 2. FUNÇÕES AUXILIARES
# ============================================

@st.cache_data(ttl=300)  # Cache de 5 minutos
def carregar_dados() -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(worksheet="Página1")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def salvar_reserva(reserva: Dict[str, Any]) -> bool:
    """Salva uma reserva no Google Sheets com tratamento de erros."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        
        # Adiciona ID único e timestamp
        reserva["ID"] = str(uuid.uuid4())[:8]
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Pendente"
        
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache para próxima leitura
        st.cache_data.clear()
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar reserva: {str(e)}")
        return False

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_nome(nome: str) -> bool:
    """Valida nome (mínimo 3 caracteres, apenas letras e espaços)."""
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    return all(c.isalpha() or c.isspace() for c in nome_limpo)

def mostrar_timer(tempo_total: int, inicio_time: float) -> tuple[bool, str]:
    """Calcula e formata o tempo restante."""
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

# ============================================
# 3. ESTADOS DA SESSÃO
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
# 4. CSS GLOBAL E COMPONENTES FIXOS
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
        position: relative; 
        margin: 0 auto;
        max-width: 1000px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .translucent-balloon { 
        background-color: rgba(50, 50, 50, 0.85); 
        padding: 25px; 
        border-radius: 15px; 
        color: white; 
        backdrop-filter: blur(10px); 
        margin-bottom: 20px; 
        border: 1px solid rgba(255,255,255,0.1); 
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
        color: #4CAF50 !important; 
        background-color: rgba(0, 0, 0, 0.5);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border-color: #4CAF50;
    }
    .icon-text { 
        font-size: 50px;
        margin-bottom: 10px; 
        transition: transform 0.3s ease;
    }
    .clean-link:hover .icon-text {
        transform: scale(1.1);
    }
    .label-text { 
        font-size: 18px; 
        font-weight: bold; 
        letter-spacing: 1px; 
        margin-bottom: 8px;
    }
    .link-description {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.3;
        margin-top: 5px;
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
        box-shadow: 3px 3px 5px #777;
    }
    .regulamento-icon { 
        display: block; 
        text-align: center; 
        margin-top: 20px; 
        text-decoration: none; 
        color: #555; 
        font-size: 14px; 
        transition: all 0.3s ease; 
        padding: 10px;
        border-radius: 8px;
        background-color: rgba(0,0,0,0.05);
    }
    .regulamento-icon span { 
        font-size: 24px; 
        display: block; 
        margin-bottom: 5px;
    }
    .regulamento-icon:hover { 
        color: #4CAF50; 
        transform: scale(1.05); 
        background-color: rgba(76, 175, 80, 0.1);
    }
    .assinatura-footer { 
        position: fixed; 
        bottom: 15px; 
        left: 20px; 
        width: 130px; 
        z-index: 9999; 
        opacity: 0.8;
        transition: opacity 0.3s ease;
    }
    .assinatura-footer:hover {
        opacity: 1;
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
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .tennis-ball-yellow {
        color: #FFFF00 !important;
        text-shadow: 0 0 10px #FF0, 0 0 20px #FF0 !important;
        filter: drop-shadow(0 0 5px rgba(255, 255, 0, 0.7));
        animation: glow 1.5s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from {
            text-shadow: 0 0 10px #FF0, 0 0 20px #FF0;
        }
        to {
            text-shadow: 0 0 15px #FF0, 0 0 25px #FF0, 0 0 35px #FF0;
        }
    }
    .stButton > button {
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        border-color: #FFFF00 !important;
    }
    /* Responsividade */
    @media (max-width: 768px) {
        .header-title { 
            font-size: 36px; 
        }
        .custom-card { 
            padding: 20px; 
            margin: 10px;
        }
        .icon-text { 
            font-size: 40px; 
        }
        .label-text { 
            font-size: 16px; 
        }
        .clean-link {
            height: 160px;
            padding: 15px;
        }
        .whatsapp-float {
            width: 50px;
            height: 50px;
            bottom: 30px;
            right: 30px;
        }
    }
    @media (max-width: 480px) {
        .header-title { 
            font-size: 28px; 
        }
        .custom-card { 
            padding: 15px; 
        }
        .icon-text { 
            font-size: 35px; 
        }
    }
</style>

<!-- Botão WhatsApp Flutuante -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank" 
   aria-label="Contato via WhatsApp">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="Ícone do WhatsApp">
</a>

<!-- Assinatura -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura André Aranha">
""", unsafe_allow_html=True)

# ============================================
# 5. MENU LATERAL - VERSÃO LIMPA E SIMPLES
# ============================================

with st.sidebar:
    # BOLA DE TÊNIS AMARELA FOSFORESCENTE 🎾
    st.markdown("<h2 style='color: #FFFF00; text-align: center; text-shadow: 0 0 10px #FF0;'>🎾 MENU</h2>", 
                unsafe_allow_html=True)
    
    # MENU LIMPO E SIMPLES - APENAS OS 5 ITENS SOLICITADOS
    menu_items = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    
    for item in menu_items:
        # Ícone de bola de tênis amarela antes de cada item
        icone = "<span class='tennis-ball-yellow'>🎾</span>"
        if st.button(f"{icone} {item}", key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    # BOLA DE TÊNIS AMARELA FOSFORESCENTE 🎾
    st.markdown("<h3 style='color: #FFFF00; text-shadow: 0 0 5px #FF0;'>🎾 ACADEMIAS RECOMENDADAS</h3>", 
                unsafe_allow_html=True)
    
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"<span class='tennis-ball-yellow'>📍</span> **{nome}**\n"
            f"<div class='sidebar-detalhe'>"
            f"{info['endereco']}<br>📞 {info['telefone']}"
            f"</div>", 
            unsafe_allow_html=True
        )

# ============================================
# 6. LÓGICA DE PÁGINAS
# ============================================

# Título principal com bola de tênis amarela
st.markdown('<div class="header-title"><span class="tennis-ball-yellow">🎾</span> TENNIS CLASS</div>', 
            unsafe_allow_html=True)

# PÁGINA: HOME
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.markdown('<h3 style="text-align: center; color: #333;"><span class="tennis-ball-yellow">🎾</span> Agendar Aula</h3>', 
                       unsafe_allow_html=True)
            
            # Campos do formulário com validação
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input(
                    "Nome do Aluno *",
                    help="Digite seu nome completo (mínimo 3 caracteres)",
                    label_visibility="visible",
                    placeholder="Ex: João Silva"
                )
            with col2:
                email = st.text_input(
                    "E-mail *",
                    help="Digite um e-mail válido para confirmação",
                    label_visibility="visible",
                    placeholder="Ex: joao.silva@email.com"
                )
            
            # Lista de serviços formatada
            servicos_lista = [
                f"{SERVICOS[key]['icone']} {SERVICOS[key]['nome']} R$ {SERVICOS[key]['preco']}"
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
            
            # Botão de submissão
            submit = st.form_submit_button(
                "🎾 AVANÇAR PARA PAGAMENTO", 
                use_container_width=True,
                type="primary"
            )
            
            if submit:
                st.session_state.erros_form = {}
                
                # Validação
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido. Use apenas letras (mínimo 3 caracteres)."
                
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido. Digite um e-mail válido."
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": dt.strftime("%d/%m/%Y"),
                        "Horário": hr,
                        "Aluno": aluno.strip(),
                        "Serviço": servico,
                        "Unidade": unidade,
                        "E-mail": email.lower().strip()
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    # Mostra erros
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', 
                                  unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        st.markdown('<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        
        # QR Code
        st.image(
            "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
            use_column_width=False,
            width=250
        )
        
        # Chave PIX
        st.markdown("""
        <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <p style="text-align: center; font-family: monospace; font-size: 18px; margin: 0;">
                <strong>aranha.corp@gmail.com</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Timer otimizado
        timer_box = st.empty()
        
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(
                TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                timer_box.markdown(
                    f'<div class="timer-warning">{mensagem_timer}</div>',
                    unsafe_allow_html=True
                )
                # Auto-refresh para atualizar o timer
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.pagamento_ativo = False
                timer_box.warning("⏰ Tempo esgotado! Por favor, inicie uma nova reserva.")
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
                    
                    # Limpa estado e aguarda para redirecionar
                    st.session_state.pagamento_ativo = False
                    st.session_state.reserva_temp = {}
                    time.sleep(3)
                    st.rerun()
    
    # Ícone do regulamento
    st.markdown("""
    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing" 
       target="_blank" 
       class="regulamento-icon" 
       title="Clique para ler o regulamento">
        <span>📄</span>
        Ler Regulamento de Uso
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: PREÇOS
elif st.session_state.pagina == "Preços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # BOLA DE TÊNIS AMARELA FOSFORESCENTE 🎾
    st.markdown('<h3 style="text-align: center; color: #333;"><span class="tennis-ball-yellow">🎾</span> Tabela de Preços</h3>', 
               unsafe_allow_html=True)
    st.markdown("---")
    
    for key, info in SERVICOS.items():
        if key == "eventos":
            st.markdown(f"<div style='margin: 15px 0; padding-left: 10px;'><span class='tennis-ball-yellow'>🎾</span> <strong>{info['nome']}:</strong> <em>Valor a combinar</em></div>")
        else:
            unidade = "/hora" if key != "competitivo" else "/mês"
            st.markdown(f"<div style='margin: 15px 0; padding-left: 10px;'><span class='tennis-ball-yellow'>🎾</span> <strong>{info['nome']}:</strong> R$ {info['preco']} {unidade}</div>")
    
    st.markdown("---")
    st.info("<span class='tennis-ball-yellow'>💡</span> *Valores sujeitos a alteração. Consulte condições especiais para pacotes.*", 
            unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;"><span class="tennis-ball-yellow">🎾</span> Portal de Cadastros</h3>', 
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
           target="_blank"
           aria-label="Cadastro de Aluno de Tênis"
           onclick="return confirm('Você será redirecionado para o formulário de cadastro de aluno. Deseja continuar?')">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
            <div class="link-description">
                Formulário para novos alunos de tênis
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Academia de Tênis"
           onclick="return confirm('Você será redirecionado para o formulário de cadastro de academia. Deseja continuar?')">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
            <div class="link-description">
                Para academias de tênis parceiras
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Professor de Tênis"
           onclick="return confirm('Você será redirecionado para o formulário de cadastro de professor. Deseja continuar?')">
            <div class="icon-text">🎾</div>
            <div class="label-text">PROFESSOR</div>
            <div class="link-description">
                Para professores de tênis parceiros
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: DASHBOARD
elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.admin_autenticado:
        st.markdown('<h3 style="text-align: center; color: #333;"><span class="tennis-ball-yellow">🎾</span> Acesso Administrativo</h3>', 
                   unsafe_allow_html=True)
        
        # Usa secrets do Streamlit
        try:
            senha_correta = st.secrets.get("ADMIN_PASSWORD", "aranha2026")
        except:
            senha_correta = "aranha2026"
        
        senha = st.text_input(
            "Digite a senha de administrador:", 
            type="password",
            label_visibility="visible",
            help="Senha para acesso ao dashboard",
            placeholder="Digite a senha..."
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔓 Acessar", use_container_width=True):
                if senha == senha_correta:
                    st.session_state.admin_autenticado = True
                    st.success("✅ Acesso concedido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        with col2:
            if st.button("🔙 Voltar para Home", use_container_width=True):
                st.session_state.pagina = "Home"
                st.rerun()
    
    else:
        st.markdown('<h3 style="text-align: center; color: #333;"><span class="tennis-ball-yellow">🎾</span> Dashboard - Reservas</h3>', 
                   unsafe_allow_html=True)
        
        # Botão de logout
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.admin_autenticado = False
                st.rerun()
        
        st.markdown("---")
        
        # Carrega e exibe dados
        try:
            df = carregar_dados()
            
            if not df.empty:
                # Formata colunas
                colunas_exibir = [col for col in df.columns if col not in ['ID', 'Timestamp']]
                df_display = df[colunas_exibir].copy()
                
                # Adiciona contadores
                total = len(df_display)
                pendentes = len(df_display[df_display['Status'] == 'Pendente'])
                confirmados = len(df_display[df_display['Status'] == 'Confirmado'])
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total, delta=f"{total} total")
                with col2:
                    st.metric("Pendentes", pendentes, 
                             delta=f"{pendentes/total*100:.1f}%" if total > 0 else "0%",
                             delta_color="inverse")
                with col3:
                    st.metric("Confirmados", confirmados,
                             delta=f"{confirmados/total*100:.1f}%" if total > 0 else "0%",
                             delta_color="normal")
                
                st.markdown("---")
                
                # Tabela interativa
                st.dataframe(
                    df_display.sort_values('Data', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Pendente", "Confirmado", "Cancelado"],
                            required=True,
                        ),
                        "Data": st.column_config.DateColumn(
                            "Data",
                            format="DD/MM/YYYY"
                        ),
                        "Horário": st.column_config.TextColumn(
                            "Horário",
                            width="small"
                        )
                    }
                )
                
                # Botões de ação
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.success("✅ Dados atualizados!")
                        time.sleep(1)
                        st.rerun()
                
                with col2:
                    csv = df_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar CSV",
                        data=csv,
                        file_name=f"reservas_tennis_class_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        type="primary"
                    )
            else:
                st.info("📭 Nenhuma reserva encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dashboard: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;"><span class="tennis-ball-yellow">🎾</span> Canais de Atendimento</h3>', 
               unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 E-mail")
        st.markdown(f"""
        <div style='padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <div style="font-size: 14px; color: #ccc;">
                <strong style="color: #4CAF50; font-size: 16px;">aranha.corp@gmail.com</strong><br>
                <span style="font-size: 13px;">Respondemos em até 24h</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown(f"""
        <div style='padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <div style="font-size: 14px; color: #ccc;">
                <strong style="color: #
