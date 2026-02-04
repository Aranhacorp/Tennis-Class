<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tennis Academy</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            background-color: #f5f5f5;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Estilo do menu */
        nav {
            background-color: #2c3e50;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        nav ul {
            list-style: none;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }

        nav a {
            color: white;
            text-decoration: none;
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }

        nav a:hover {
            background-color: #34495e;
        }

        /* Layout principal */
        .container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }

        /* Seção de aulas */
        .aulas-section {
            margin-bottom: 30px;
        }

        .aulas-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        .aula-item {
            background-color: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }

        .aula-item:hover {
            transform: translateY(-5px);
        }

        .aula-titulo {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        /* Balões de preço com cinza transparente */
        .preco-balao {
            display: inline-block;
            background-color: rgba(128, 128, 128, 0.2); /* Cinza com 20% de opacidade */
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin: 15px 0;
            border: 2px solid rgba(128, 128, 128, 0.3);
            backdrop-filter: blur(5px);
        }

        .aula-descricao {
            color: #666;
            line-height: 1.6;
            margin-top: 10px;
        }

        /* Seção academias */
        .academias-section {
            margin-top: 30px;
        }

        .academias-container {
            display: grid;
            gap: 20px;
        }

        .academia-item {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .academia-nome {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.2em;
        }

        .academia-endereco, .academia-telefone {
            color: #666;
            margin: 5px 0;
        }

        /* Seção treinamento */
        .treinamento-section {
            background-color: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 30px;
            grid-column: 1 / -1;
        }

        .treinamento-titulo {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        /* Responsividade */
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            
            nav ul {
                flex-direction: column;
                align-items: center;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <!-- Menu de navegação -->
    <nav>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#precos">Preços</a></li>
            <li><a href="#cadastro">Cadastro</a></li>
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#contato">Contato</a></li>
        </ul>
    </nav>

    <div class="container">
        <!-- Seção de Aulas -->
        <div class="aulas-section">
            <h2 style="color: #2c3e50; margin-bottom: 20px; font-size: 2em;">Aulas</h2>
            
            <div class="aulas-container">
                <div class="aula-item">
                    <h3 class="aula-titulo">Aula particular</h3>
                    <div class="preco-balao">R$ 250 /hora</div>
                    <p class="aula-descricao">Aula individual com foco total no aluno. Perfeita para quem quer evoluir rapidamente com atenção personalizada.</p>
                </div>
                
                <div class="aula-item">
                    <h3 class="aula-titulo">Aula em grupo</h3>
                    <div class="preco-balao">R$ 200 /hora</div>
                    <p class="aula-descricao">Aula em grupo de até 4 pessoas. Ideal para amigos ou familiares que querem aprender juntos de forma divertida.</p>
                </div>
            </div>
        </div>

        <!-- Seção de Academias -->
        <div class="academias-section">
            <h2 style="color: #2c3e50; margin-bottom: 20px; font-size: 2em;">Academias</h2>
            
            <div class="academias-container">
                <div class="academia-item">
                    <h3 class="academia-nome">PLAY TENNIS Ibirapuera</h3>
                    <p class="academia-endereco">R. Estado de Israel, 860 - SP</p>
                    <p class="academia-telefone">(11) 97752-0488</p>
                </div>
                
                <div class="academia-item">
                    <h3 class="academia-nome">TOP One Tennis</h3>
                    <p class="academia-endereco">Av. Indianópolis, 647 - SP</p>
                    <p class="academia-telefone">(11) 93236-3828</p>
                </div>
                
                <div class="academia-item">
                    <h3 class="academia-nome">MELL Tennis</h3>
                    <p class="academia-endereco">Endereço e telefone em breve</p>
                </div>
            </div>
        </div>

        <!-- Seção Treinamento -->
        <div class="treinamento-section">
            <h2 class="treinamento-titulo">Treinamento</h2>
            <p style="color: #666; line-height: 1.6;">Nossos treinamentos são desenvolvidos por profissionais certificados e adaptados para todas as idades e níveis, desde iniciantes até jogadores avançados. Oferecemos programas personalizados que incluem técnica, tática, condicionamento físico e preparação mental.</p>
        </div>
    </div>

    <script>
        // Adiciona interatividade aos itens
        document.querySelectorAll('.aula-item, .academia-item').forEach(item => {
            item.addEventListener('click', function() {
                this.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 200);
            });
        });
        
        // Adiciona efeito de hover nos balões de preço
        document.querySelectorAll('.preco-balao').forEach(balao => {
            balao.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(128, 128, 128, 0.3)';
                this.style.transform = 'scale(1.05)';
            });
            
            balao.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'rgba(128, 128, 128, 0.2)';
                this.style.transform = 'scale(1)';
            });
        });
    </script>
</body>
</html>
