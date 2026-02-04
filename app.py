import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Tennis Academy - Aulas de Tênis",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dados das aulas
AULAS = [
    {
        'id': 1,
        'titulo': 'Aula Particular',
        'preco': 'R$ 250 /hora',
        'descricao': 'Aula individual com foco total no aluno. Perfeita para quem quer evoluir rapidamente com atenção personalizada.',
        'beneficios': [
            'Professor dedicado exclusivamente a você',
            'Plano de treino personalizado',
            'Horários flexíveis',
            'Feedback detalhado a cada aula'
        ],
        'icone': '🎯'
    },
    {
        'id': 2,
        'titulo': 'Aula em Grupo',
        'preco': 'R$ 200 /hora',
        'descricao': 'Aula em grupo de até 4 pessoas. Ideal para amigos ou familiares que querem aprender juntos de forma divertida.',
        'beneficios': [
            'Economia de até 20% por pessoa',
            'Ambiente descontraído e social',
            'Jogos e exercícios em equipe',
            'Perfeito para todos os níveis'
        ],
        'icone': '👥'
    }
]

# Dados das academias
ACADEMIAS = [
    {
        'nome': 'PLAY TENNIS Ibirapuera',
        'endereco': 'R. Estado de Israel, 860 - Vila Clementino, São Paulo - SP',
        'telefone': '(11) 97752-0488',
        'horario': 'Segunda a Sábado: 6h às 22h | Domingo: 8h às 18h',
        'icone': '📍'
    },
    {
        'nome': 'TOP One Tennis',
        'endereco': 'Av. Indianópolis, 647 - Indianópolis, São Paulo - SP',
        'telefone': '(11) 93236-3828',
        'horario': 'Segunda a Sexta: 7h às 23h | Sábado: 8h às 20h',
        'icone': '📍'
    },
    {
        'nome': 'MELL Tennis',
        'endereco': 'Em breve - Nova unidade',
        'telefone': 'Informações em breve',
        'horario': 'Horários a definir',
        'icone': '📍'
    }
]

# CSS personalizado
st.markdown("""
<style>
    /* Estilos gerais */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Cabeçalho */
    .header {
        background: linear-gradient(135deg, #2c3e50 0%, #4a6491 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    /* Cards de aula */
    .aula-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #3498db;
        transition: transform 0.3s;
    }
    
    .aula-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    
    /* Balões de preço em cinza transparente */
    .price-badge {
        display: inline-block;
        background-color: rgba(128, 128, 128, 0.15);
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 10px 0;
        border: 2px solid rgba(128, 128, 128, 0.25);
    }
    
    /* Cards de academia */
    .academia-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    
    /* Seção de contato */
    .contact-info {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2ecc71;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .header {
            padding: 1rem;
        }
        
        .price-badge {
            font-size: 1rem;
            padding: 8px 16px;
        }
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Função para renderizar card de aula
def render_aula_card(aula):
    st.markdown(f"""
    <div class="aula-card fade-in">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 1.5rem;">{aula['icone']}</span>
            <h3 style="margin: 0;">{aula['titulo']}</h3>
        </div>
        <div class="price-badge">{aula['preco']}</div>
        <p>{aula['descricao']}</p>
        <ul style="color: #555;">
    """, unsafe_allow_html=True)
    
    for beneficio in aula['beneficios']:
        st.markdown(f"<li>✓ {beneficio}</li>", unsafe_allow_html=True)
    
    st.markdown("</ul>", unsafe_allow_html=True)
    
    # Botão de agendamento
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"Agendar {aula['titulo']}", key=f"agendar_{aula['id']}"):
            st.session_state[f'aula_selecionada'] = aula['titulo']
            st.success(f"Você selecionou: {aula['titulo']}! Em breve entraremos em contato.")

# Função para renderizar card de academia
def render_academia_card(academia):
    st.markdown(f"""
    <div class="academia-card fade-in">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.2rem;">{academia['icone']}</span>
            <h4 style="margin: 0; color: #2c3e50;">{academia['nome']}</h4>
        </div>
        <p style="margin: 5px 0; color: #666;">📍 {academia['endereco']}</p>
        <p style="margin: 5px 0; color: #666;">📞 {academia['telefone']}</p>
        <p style="margin: 5px 0; color: #777;">🕒 {academia['horario']}</p>
    </div>
    """, unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎾 Tennis Academy</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Menu Principal",
        ["🏠 Home", "💰 Preços", "📝 Cadastro", "📊 Dashboard", "📞 Contato"]
    )
    
    st.markdown("---")
    st.markdown("### 📅 Agendamento Rápido")
    
    tipo_aula = st.selectbox(
        "Tipo de Aula",
        ["Aula Particular", "Aula em Grupo"]
    )
    
    data = st.date_input("Data")
    horario = st.time_input("Horário")
    
    if st.button("✅ Confirmar Agendamento", type="primary"):
        st.success(f"Aula {tipo_aula} agendada para {data} às {horario}!")
    
    st.markdown("---")
    st.markdown("### 🔔 Novidades")
    st.info("🎯 **Novo Pacote Gold:** 5 aulas por R$ 1.100!")
    st.info("👥 **Grupos Especiais:** Traga 3 amigos e ganhe 20% de desconto!")

# Conteúdo principal baseado na seleção do menu
if menu == "🏠 Home":
    # Cabeçalho
    st.markdown("""
    <div class="header fade-in">
        <h1 style="color: white; margin: 0;">🎾 Tennis Academy</h1>
        <p style="color: #e0e0e0; font-size: 1.2rem;">Excelência no ensino de tênis desde 2010</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Seção de Aulas
    st.markdown("<h2>🎯 Nossas Aulas</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_aula_card(AULAS[0])
    
    with col2:
        render_aula_card(AULAS[1])
    
    # Seção de Academias
    st.markdown("<h2>📍 Nossas Academias</h2>", unsafe_allow_html=True)
    
    for academia in ACADEMIAS:
        render_academia_card(academia)
    
    # Mapa (simulado)
    st.markdown("### 🗺️ Localização das Academias")
    st.map(pd.DataFrame({
        'lat': [-23.587, -23.595, -23.580],
        'lon': [-46.660, -46.665, -46.670],
        'name': ['PLAY TENNIS Ibirapuera', 'TOP One Tennis', 'MELL Tennis']
    }))
    
    # Seção de Treinamento
    st.markdown("<h2>💪 Nosso Método de Treinamento</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem;">🎯</div>
            <h4>Técnica</h4>
            <p style="font-size: 0.9rem; color: #666;">Fundamentos sólidos e movimentos precisos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem;">♟️</div>
            <h4>Tática</h4>
            <p style="font-size: 0.9rem; color: #666;">Estratégias de jogo e posicionamento</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem;">🏃</div>
            <h4>Condicionamento</h4>
            <p style="font-size: 0.9rem; color: #666;">Preparo físico específico para tênis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem;">🧠</div>
            <h4>Mental</h4>
            <p style="font-size: 0.9rem; color: #666;">Foco, concentração e controle emocional</p>
        </div>
        """, unsafe_allow_html=True)

elif menu == "💰 Preços":
    st.markdown("<h1>💰 Nossos Preços e Pacotes</h1>", unsafe_allow_html=True)
    
    # Tabela de preços
    st.markdown("<h3>📋 Tabela de Preços</h3>", unsafe_allow_html=True)
    
    precos_df = pd.DataFrame({
        'Aula': ['Aula Particular', 'Aula em Grupo', 'Pacote Gold (5 aulas)', 'Pacote Silver (5 aulas grupo)'],
        'Preço': ['R$ 250 / hora', 'R$ 200 / hora', 'R$ 1.100 (economia de R$ 150)', 'R$ 900 (economia de R$ 100)'],
        'Duração': ['1 hora', '1 hora', '5 horas', '5 horas'],
        'Vantagens': [
            'Atenção personalizada',
            'Socialização e economia',
            'Análise de vídeo + relatório',
            'Grupo fixo + material incluso'
        ]
    })
    
    st.dataframe(precos_df, use_container_width=True, hide_index=True)
    
    # Pacotes especiais
    st.markdown("<h3>🎁 Pacotes Especiais</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="aula-card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <h3 style="color: #2c3e50;">👑 Pacote Gold</h3>
            <div class="price-badge" style="background-color: rgba(255, 215, 0, 0.2);">R$ 1.100</div>
            <p>5 aulas particulares com benefícios exclusivos:</p>
            <ul style="color: #555;">
                <li>✓ 5 aulas de 1 hora cada</li>
                <li>✓ Análise de vídeo profissional</li>
                <li>✓ Relatório de evolução</li>
                <li>✓ Acesso à sala VIP</li>
                <li>✓ Bola oficial de competição</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Comprar Pacote Gold", key="gold"):
            st.success("Pacote Gold selecionado! Em breve enviaremos os detalhes.")
    
    with col2:
        st.markdown("""
        <div class="aula-card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <h3 style="color: #2c3e50;">⭐ Pacote Silver</h3>
            <div class="price-badge" style="background-color: rgba(192, 192, 192, 0.2);">R$ 900</div>
            <p>5 aulas em grupo com economia:</p>
            <ul style="color: #555;">
                <li>✓ 5 aulas em grupo de 1 hora</li>
                <li>✓ Grupo fixo de até 4 pessoas</li>
                <li>✓ Material didático incluso</li>
                <li>✓ Bolas oficiais de competição</li>
                <li>✓ Certificado de participação</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Comprar Pacote Silver", key="silver"):
            st.success("Pacote Silver selecionado! Em breve enviaremos os detalhes.")

elif menu == "📝 Cadastro":
    st.markdown("<h1>📝 Cadastro de Aluno</h1>", unsafe_allow_html=True)
    
    # Formulário de cadastro
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo *")
            email = st.text_input("E-mail *")
            cpf = st.text_input("CPF")
        
        with col2:
            telefone = st.text_input("Telefone *")
            data_nascimento = st.date_input("Data de Nascimento")
            nivel = st.selectbox("Nível de Tênis", ["Iniciante", "Intermediário", "Avançado", "Competitivo"])
        
        endereco = st.text_input("Endereço")
        
        col3, col4 = st.columns(2)
        with col3:
            tipo_aula = st.selectbox(
                "Tipo de Aula Preferida",
                ["Aula Particular", "Aula em Grupo", "Ainda não sei"]
            )
        
        with col4:
            academia_preferida = st.selectbox(
                "Academia Preferida",
                ["PLAY TENNIS Ibirapuera", "TOP One Tennis", "Indiferente"]
            )
        
        observacoes = st.text_area("Observações ou Objetivos")
        
        termos = st.checkbox("Aceito os termos e condições *")
        
        submitted = st.form_submit_button("Cadastrar", type="primary")
        
        if submitted:
            if nome and email and telefone and termos:
                st.success("🎉 Cadastro realizado com sucesso!")
                st.balloons()
                
                # Mostrar resumo
                st.markdown("### 📋 Resumo do Cadastro")
                st.info(f"""
                **Nome:** {nome}  
                **E-mail:** {email}  
                **Telefone:** {telefone}  
                **Nível:** {nivel}  
                **Aula Preferida:** {tipo_aula}  
                **Academia:** {academia_preferida}
                
                Em breve entraremos em contato para confirmar seu cadastro!
                """)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (*)")

elif menu == "📊 Dashboard":
    st.markdown("<h1>📊 Dashboard de Desempenho</h1>", unsafe_allow_html=True)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Alunos", "247", "+12%")
    
    with col2:
        st.metric("Aulas Realizadas", "1,548", "+8%")
    
    with col3:
        st.metric("Satisfação", "96%", "+2%")
    
    with col4:
        st.metric("Novos Alunos", "38", "+15%")
    
    # Gráficos
    st.markdown("### 📈 Estatísticas Mensais")
    
    # Dados fictícios para gráficos
    import numpy as np
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    aulas_particulares = np.random.randint(20, 50, 12)
    aulas_grupo = np.random.randint(30, 70, 12)
    
    chart_data = pd.DataFrame({
        'Mês': meses,
        'Aulas Particulares': aulas_particulares,
        'Aulas em Grupo': aulas_grupo
    })
    
    st.bar_chart(chart_data.set_index('Mês'))
    
    # Distribuição por nível
    st.markdown("### 🎯 Distribuição por Nível")
    
    niveis = ['Iniciante', 'Intermediário', 'Avançado', 'Competitivo']
    quantidade = [45, 80, 70, 52]
    
    nivel_df = pd.DataFrame({
        'Nível': niveis,
        'Alunos': quantidade
    })
    
    st.bar_chart(nivel_df.set_index('Nível'))
    
    # Tabela de próximas aulas
    st.markdown("### 📅 Próximas Aulas Agendadas")
    
    proximas_aulas = pd.DataFrame({
        'Data/Hora': ['15/11 09:00', '15/11 14:00', '16/11 10:00', '16/11 16:00', '17/11 11:00'],
        'Aluno': ['Carlos Silva', 'Ana Souza', 'Pedro Santos', 'Maria Oliveira', 'João Costa'],
        'Tipo': ['Particular', 'Grupo', 'Particular', 'Grupo', 'Particular'],
        'Academia': ['Ibirapuera', 'Indianópolis', 'Ibirapuera', 'Ibirapuera', 'Indianópolis'],
        'Status': ['Confirmada', 'Confirmada', 'Pendente', 'Confirmada', 'Confirmada']
    })
    
    st.dataframe(proximas_aulas, use_container_width=True, hide_index=True)

elif menu == "📞 Contato":
    st.markdown("<h1>📞 Entre em Contato</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="contact-info fade-in">
            <h3>📞 Telefones</h3>
            <p><strong>Central de Atendimento:</strong><br>(11) 98765-4321</p>
            <p><strong>WhatsApp:</strong><br>(11) 98765-4321</p>
            <p><strong>Emergências:</strong><br>(11) 99999-8888</p>
            
            <h3>📧 E-mails</h3>
            <p><strong>Geral:</strong><br>contato@tennisacademy.com</p>
            <p><strong>Matrículas:</strong><br>matriculas@tennisacademy.com</p>
            <p><strong>Financeiro:</strong><br>financeiro@tennisacademy.com</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="contact-info fade-in">
            <h3>📍 Endereços</h3>
            <p><strong>PLAY TENNIS Ibirapuera:</strong><br>R. Estado de Israel, 860 - SP</p>
            <p><strong>TOP One Tennis:</strong><br>Av. Indianópolis, 647 - SP</p>
            <p><strong>Horário de Funcionamento:</strong><br>Segunda a Sábado: 6h às 22h</p>
            
            <h3>🌐 Redes Sociais</h3>
            <p>📱 Instagram: @tennisacademy</p>
            <p>📘 Facebook: /tennisacademy</p>
            <p>📺 YouTube: Tennis Academy Oficial</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Formulário de contato
    st.markdown("<h3>✉️ Envie sua Mensagem</h3>", unsafe_allow_html=True)
    
    with st.form("form_contato"):
        nome_contato = st.text_input("Seu Nome *")
        email_contato = st.text_input("Seu E-mail *")
        assunto = st.selectbox("Assunto", [
            "Dúvidas sobre aulas",
            "Informações sobre preços",
            "Agendamento de aula experimental",
            "Sugestões ou reclamações",
            "Outros"
        ])
        mensagem = st.text_area("Mensagem *", height=150)
        
        enviar = st.form_submit_button("Enviar Mensagem", type="primary")
        
        if enviar:
            if nome_contato and email_contato and mensagem:
                st.success("✅ Mensagem enviada com sucesso! Responderemos em até 24h.")
                st.balloons()
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (*)")

# Rodapé
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🎾 <strong>Tennis Academy</strong> - Excelência no ensino de tênis desde 2010</p>
        <p>© 2024 Tennis Academy. Todos os direitos reservados.</p>
    </div>
    """, unsafe_allow_html=True)
