elif menu == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Cadastro de Professor</h2>", unsafe_allow_html=True)
    
    # URL que você forneceu, com o parâmetro de incorporação adicionado ao final
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true"
    
    # Criando o quadro (iframe) para exibir o formulário dentro do App
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe src="{form_url}" width="100%" height="800" frameborder="0" marginheight="0" marginwidth="0" 
            style="background-color: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 800px;">
            Carregando formulário...</iframe>
        </div>
    """, unsafe_allow_html=True)
