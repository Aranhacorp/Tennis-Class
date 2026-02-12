# ==============================================
# MASTER CODE DEEP SEEK v.12
# APP: TENNIS CLASS - Gestão de aulas e eventos
# CORREÇÕES: Aula Kids R$ 230/hora | Pacote 4h R$ 920
# ESTÁVEL - TODOS OS ELEMENTOS PRESERVADOS
# ==============================================

import streamlit as st

# ---------- CONFIGURAÇÃO INICIAL ----------
st.set_page_config(
    page_title="Tennis Class",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SIDEBAR ----------
with st.sidebar:
    # MENU DE NAVEGAÇÃO
    st.header("MENU")
    menu = st.radio(
        "Navegação",
        ["Home", "Preços", "Cadastro", "Dashboard"],
        label_visibility="collapsed"
    )
    st.markdown("---")

    # CONTATO
    st.header("Contato")
    st.markdown("📞 (11) 99999-9999")
    st.markdown("✉️ contato@tennisclass.com")
    st.markdown("---")

    # ---------- PREÇOS (BARRA LATERAL) ----------
    st.subheader("Aula particular")
    st.markdown("**R$ 250/hora**")

    st.subheader("Pacote aula particular")
    st.markdown("**R$ 1000 / 4 aulas de 1 hora**")

    st.subheader("Aula em grupo")
    st.markdown("**R$ 200/hora**")

    st.subheader("Pacote aula em grupo")
    st.markdown("**R$ 800 / 4 aulas de 1 hora**")

    # ---------- CORREÇÃO APLICADA ----------
    st.subheader("Aula Kids")
    st.markdown("**R$ 230/hora**")  # ✅ CORRIGIDO

    st.subheader("Pacote aula particular")
    st.markdown("**R$ 2000 / 8 aulas de 1 hora**")

    st.subheader("Personal trainer")
    st.markdown("**R$ 250/hora**")

    st.subheader("Pacote aula em grupo")
    st.markdown("**R$ 1600 / 8 aulas de 1 hora**")

    st.subheader("Eventos")
    st.markdown("**R$ 0/hora**")

    # ---------- CORREÇÃO APLICADA ----------
    st.subheader("Pacote aula Kids")
    st.markdown("**R$ 920 / 4 aulas de 1 hora**")  # ✅ CORRIGIDO

    st.subheader("Treinamento Competitivo")
    st.markdown("** **")

    st.subheader("Pacote Personal Trainer")
    st.markdown("** **")
    st.markdown("---")

    # ---------- ACADEMIAS PARCEIRAS ----------
    st.header("ACADEMIAS PARCEIRAS")
    st.markdown(
        "**PLAY TENNIS Ibirapuera**  \n"
        "R. Estado de Israel, 860 - SP  \n"
        "(11) 97752-0488"
    )
    st.markdown(
        "**TOP One Tennis**  \n"
        "Av. Indianópolis, 647 - SP  \n"
        "(11) 93236-3828"
    )
    st.markdown("**MELL Tennis**")

# ---------- CONTEÚDO PRINCIPAL ----------
if menu == "Home":
    st.title("🎾 Bem‑vindo ao Tennis Class")
    st.markdown(
        "Sua plataforma completa para gestão de aulas e eventos de tênis. "
        "Aqui você encontra professores, academias parceiras e toda a estrutura "
        "para evoluir no esporte."
    )
    st.image(
        "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
        caption="Tênis para todos os níveis",
        use_container_width=True
    )

elif menu == "Preços":
    st.title("💰 Tabela de Preços")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Aula particular")
        st.write("R$ 250/hora")

        st.subheader("Pacote aula particular (4h)")
        st.write("R$ 1000 / 4 aulas")

        st.subheader("Aula em grupo")
        st.write("R$ 200/hora")

        st.subheader("Pacote aula em grupo (4h)")
        st.write("R$ 800 / 4 aulas")

        st.subheader("Aula Kids")
        st.write("R$ 230/hora")  # ✅ CORRIGIDO

    with col2:
        st.subheader("Pacote aula particular (8h)")
        st.write("R$ 2000 / 8 aulas")

        st.subheader("Personal trainer")
        st.write("R$ 250/hora")

        st.subheader("Pacote aula em grupo (8h)")
        st.write("R$ 1600 / 8 aulas")

        st.subheader("Eventos")
        st.write("R$ 0/hora")

        st.subheader("Pacote aula Kids")
        st.write("R$ 920 / 4 aulas")  # ✅ CORRIGIDO

        st.subheader("Treinamento Competitivo")
        st.write("Consultar")

        st.subheader("Pacote Personal Trainer")
        st.write("Consultar")

elif menu == "Cadastro":
    st.title("📋 Cadastro de Alunos")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo")
        idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone")
        tipo_aula = st.selectbox(
            "Tipo de aula",
            ["Aula particular", "Aula em grupo", "Aula Kids", "Personal trainer", "Eventos"]
        )
        enviado = st.form_submit_button("Cadastrar")

        if enviado:
            st.success("✅ Aluno cadastrado com sucesso (modo simulação)")

elif menu == "Dashboard":
    st.title("📊 Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de alunos", "45", "+5")
    with col2:
        st.metric("Aulas realizadas (mês)", "128", "+12")
    with col3:
        st.metric("Receita mensal", "R$ 32.500", "+R$ 2.100")

    # Gráfico de exemplo
    st.bar_chart(
        {"Aulas": [20, 35, 18, 25]},
        use_container_width=True
    )
