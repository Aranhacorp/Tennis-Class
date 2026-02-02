<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Tennis - Academia de Tênis</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header e Menu */
        header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 28px;
            font-weight: 700;
            color: #3498db;
        }
        
        .logo span {
            color: #e74c3c;
        }
        
        nav ul {
            display: flex;
            list-style: none;
        }
        
        nav ul li {
            margin-left: 30px;
        }
        
        nav ul li a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            font-size: 18px;
            transition: color 0.3s;
        }
        
        nav ul li a:hover {
            color: #3498db;
        }
        
        /* Conteúdo Principal */
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin: 40px 0;
        }
        
        /* Seção de Academias */
        .academias-section {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }
        
        .section-title {
            font-size: 26px;
            color: #2c3e50;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }
        
        .academia-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            border-left: 5px solid #3498db;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .academia-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .academia-nome {
            font-size: 22px;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        
        .academia-nome i {
            color: #e74c3c;
            margin-right: 10px;
        }
        
        .academia-endereco, .academia-telefone {
            margin-bottom: 8px;
            color: #555;
            display: flex;
            align-items: center;
        }
        
        .academia-endereco i, .academia-telefone i {
            color: #3498db;
            margin-right: 10px;
            width: 20px;
        }
        
        /* Portal de Cadastros */
        .cadastro-section {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
        }
        
        .cadastro-options {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .cadastro-option {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        
        .cadastro-option:hover {
            border-color: #3498db;
            background-color: #e3f2fd;
        }
        
        .cadastro-icon {
            font-size: 40px;
            color: #3498db;
            margin-bottom: 15px;
        }
        
        .cadastro-title {
            font-size: 22px;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .cadastro-desc {
            color: #666;
            margin-bottom: 20px;
        }
        
        .btn-cadastro {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 12px 25px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background-color 0.3s;
        }
        
        .btn-cadastro:hover {
            background-color: #2980b9;
        }
        
        /* Footer */
        footer {
            background-color: #2c3e50;
            color: white;
            padding: 30px 0;
            margin-top: 50px;
            text-align: center;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        
        .footer-links a {
            color: #3498db;
            margin: 0 15px;
            text-decoration: none;
        }
        
        .footer-links a:hover {
            text-decoration: underline;
        }
        
        /* Responsividade */
        @media (max-width: 992px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            nav ul li {
                margin-left: 20px;
            }
        }
        
        @media (max-width: 768px) {
            .header-container {
                flex-direction: column;
                text-align: center;
            }
            
            nav ul {
                margin-top: 20px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            nav ul li {
                margin: 10px 15px;
            }
            
            .cadastro-options {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header com Menu -->
    <header>
        <div class="container header-container">
            <div class="logo">TENNIS<span>PRO</span></div>
            <nav>
                <ul>
                    <li><a href="#"><i class="fas fa-home"></i> Home</a></li>
                    <li><a href="#"><i class="fas fa-tag"></i> Preços</a></li>
                    <li><a href="#cadastro"><i class="fas fa-user-plus"></i> Cadastro</a></li>
                    <li><a href="#"><i class="fas fa-chart-bar"></i> Dashboard</a></li>
                    <li><a href="#"><i class="fas fa-envelope"></i> Contato</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="container">
        <!-- Conteúdo Principal -->
        <div class="main-content">
            <!-- Seção de Academias Recomendadas -->
            <section class="academias-section">
                <h2 class="section-title">ACADEMIAS RECOMENDADAS</h2>
                
                <div class="academia-card">
                    <h3 class="academia-nome"><i class="fas fa-tennis-ball"></i> PLAY TENNIS Ibirapuera</h3>
                    <p class="academia-endereco"><i class="fas fa-map-marker-alt"></i> R. Estado de Israel, 860 - São Paulo, SP</p>
                    <p class="academia-telefone"><i class="fas fa-phone"></i> (11) 97752-0488</p>
                </div>
                
                <div class="academia-card">
                    <h3 class="academia-nome"><i class="fas fa-tennis-ball"></i> TOP One Tennis</h3>
                    <p class="academia-endereco"><i class="fas fa-map-marker-alt"></i> Av. Indianópolis, 647 - São Paulo, SP</p>
                    <p class="academia-telefone"><i class="fas fa-phone"></i> (11) 93236-3828</p>
                </div>
                
                <div class="academia-card">
                    <h3 class="academia-nome"><i class="fas fa-tennis-ball"></i> MELL Tennis</h3>
                    <p class="academia-endereco"><i class="fas fa-map-marker-alt"></i> Endereço não informado</p>
                    <p class="academia-telefone"><i class="fas fa-phone"></i> Telefone não informado</p>
                </div>
            </section>
            
            <!-- Seção de Cadastro -->
            <section class="cadastro-section" id="cadastro">
                <h2 class="section-title">Portal de Cadastros</h2>
                
                <div class="cadastro-options">
                    <!-- Cadastro de Aluno -->
                    <div class="cadastro-option">
                        <div class="cadastro-icon">
                            <i class="fas fa-user-graduate"></i>
                        </div>
                        <h3 class="cadastro-title">ALUNO</h3>
                        <p class="cadastro-desc">Cadastre-se como aluno para acessar aulas, agendamentos e acompanhar seu progresso.</p>
                        <a href="https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog" 
                           target="_blank" class="btn-cadastro">
                            Cadastrar como Aluno
                        </a>
                    </div>
                    
                    <!-- Cadastro de Academia -->
                    <div class="cadastro-option">
                        <div class="cadastro-icon">
                            <i class="fas fa-building"></i>
                        </div>
                        <h3 class="cadastro-title">ACADEMIA</h3>
                        <p class="cadastro-desc">Cadastre sua academia para divulgar seus serviços, quadras e professores.</p>
                        <a href="https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?usp=dialog" 
                           target="_blank" class="btn-cadastro">
                            Cadastrar Academia
                        </a>
                    </div>
                    
                    <!-- Cadastro de Professor -->
                    <div class="cadastro-option">
                        <div class="cadastro-icon">
                            <i class="fas fa-chalkboard-teacher"></i>
                        </div>
                        <h3 class="cadastro-title">PROFESSOR</h3>
                        <p class="cadastro-desc">Cadastre-se como professor para oferecer aulas e gerenciar seus horários.</p>
                        <!-- Link do professor - usando o mesmo do aluno por falta de um terceiro link específico -->
                        <a href="https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog" 
                           target="_blank" class="btn-cadastro">
                            Cadastrar como Professor
                        </a>
                        <p style="margin-top: 10px; font-size: 14px; color: #777;">(Link temporário - usar formulário específico quando disponível)</p>
                    </div>
                </div>
            </section>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <div class="container">
            <p>&copy; 2023 TennisPro - Portal de Tênis. Todos os direitos reservados.</p>
            <div class="footer-links">
                <a href="#">Política de Privacidade</a>
                <a href="#">Termos de Uso</a>
                <a href="#">Contato</a>
            </div>
        </div>
    </footer>

    <script>
        // Adicionar interação aos cards de academia
        document.querySelectorAll('.academia-card').forEach(card => {
            card.addEventListener('click', function() {
                alert('Em uma implementação real, isso levaria à página da academia.');
            });
        });
        
        // Verificar se os formulários estão acessíveis
        window.addEventListener('load', function() {
            const formLinks = document.querySelectorAll('.btn-cadastro');
            
            formLinks.forEach(link => {
                // Em uma implementação real, aqui poderíamos verificar se o link está acessível
                console.log('Link de formulário:', link.href);
            });
        });
    </script>
</body>
</html>
