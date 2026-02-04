<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tennis Academy - Aulas de Tênis Profissionais</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
</head>
<body>
    <!-- Menu de Navegação -->
    <nav class="navbar">
        <div class="container nav-container">
            <a href="/" class="logo">
                <i class="fas fa-tennis-ball logo-icon"></i>
                Tennis Academy
            </a>
            
            <ul class="nav-links">
                <li><a href="/" class="{{ 'active' if request.path == '/' else '' }}">
                    <i class="fas fa-home"></i> Home
                </a></li>
                <li><a href="/precos" class="{{ 'active' if request.path == '/precos' else '' }}">
                    <i class="fas fa-tag"></i> Preços
                </a></li>
                <li><a href="/cadastro" class="{{ 'active' if request.path == '/cadastro' else '' }}">
                    <i class="fas fa-user-plus"></i> Cadastro
                </a></li>
                <li><a href="/dashboard" class="{{ 'active' if request.path == '/dashboard' else '' }}">
                    <i class="fas fa-chart-line"></i> Dashboard
                </a></li>
                <li><a href="/contato" class="{{ 'active' if request.path == '/contato' else '' }}">
                    <i class="fas fa-envelope"></i> Contato
                </a></li>
            </ul>
        </div>
    </nav>

    <!-- Conteúdo Principal -->
    <main class="main-content">
        <div class="container">
            <!-- Seção de Aulas -->
            <section class="aulas-section">
                <h2 class="section-title">
                    <i class="fas fa-graduation-cap"></i> Nossas Aulas
                </h2>
                
                <div class="aulas-grid">
                    <!-- Aula Particular -->
                    <div class="aula-card">
                        <h3 class="aula-title">
                            <i class="fas fa-user"></i> Aula Particular
                        </h3>
                        <div class="price-badge">R$ 250 / hora</div>
                        <p class="aula-description">
                            Aula individual com foco total no aluno. Perfeita para quem quer evoluir rapidamente 
                            com atenção personalizada do professor. Inclui análise de vídeo e plano de desenvolvimento individual.
                        </p>
                        <ul class="aula-benefits" style="margin-top: 1rem; padding-left: 1.2rem; color: #555;">
                            <li>Professor dedicado exclusivamente a você</li>
                            <li>Plano de treino personalizado</li>
                            <li>Horários flexíveis</li>
                            <li>Feedback detalhado a cada aula</li>
                        </ul>
                    </div>
                    
                    <!-- Aula em Grupo -->
                    <div class="aula-card">
                        <h3 class="aula-title">
                            <i class="fas fa-users"></i> Aula em Grupo
                        </h3>
                        <div class="price-badge">R$ 200 / hora</div>
                        <p class="aula-description">
                            Aula em grupo de até 4 pessoas. Ideal para amigos ou familiares que querem aprender 
                            juntos de forma divertida e econômica. Promove interação e competição saudável.
                        </p>
                        <ul class="aula-benefits" style="margin-top: 1rem; padding-left: 1.2rem; color: #555;">
                            <li>Economia de até 20% por pessoa</li>
                            <li>Ambiente descontraído e social</li>
                            <li>Jogos e exercícios em equipe</li>
                            <li>Perfeito para todos os níveis</li>
                        </ul>
                    </div>
                </div>
            </section>
            
            <!-- Seção de Academias -->
            <section class="academias-section">
                <h2 class="section-title">
                    <i class="fas fa-map-marker-alt"></i> Nossas Academias
                </h2>
                
                <div class="academias-list">
                    <!-- PLAY TENNIS Ibirapuera -->
                    <div class="academia-item">
                        <h3 class="academia-name">
                            <i class="fas fa-tennis-ball academia-icon"></i> PLAY TENNIS Ibirapuera
                        </h3>
                        <p class="academia-address">
                            <i class="fas fa-map-pin"></i> R. Estado de Israel, 860 - Vila Clementino, São Paulo - SP
                        </p>
                        <p class="academia-phone">
                            <i class="fas fa-phone"></i> (11) 97752-0488
                        </p>
                        <p class="academia-hours" style="color: #777; margin-top: 0.5rem;">
                            <i class="fas fa-clock"></i> Segunda a Sábado: 6h às 22h | Domingo: 8h às 18h
                        </p>
                    </div>
                    
                    <!-- TOP One Tennis -->
                    <div class="academia-item">
                        <h3 class="academia-name">
                            <i class="fas fa-tennis-ball academia-icon"></i> TOP One Tennis
                        </h3>
                        <p class="academia-address">
                            <i class="fas fa-map-pin"></i> Av. Indianópolis, 647 - Indianópolis, São Paulo - SP
                        </p>
                        <p class="academia-phone">
                            <i class="fas fa-phone"></i> (11) 93236-3828
                        </p>
                        <p class="academia-hours" style="color: #777; margin-top: 0.5rem;">
                            <i class="fas fa-clock"></i> Segunda a Sexta: 7h às 23h | Sábado: 8h às 20h
                        </p>
                    </div>
                    
                    <!-- MELL Tennis -->
                    <div class="academia-item">
                        <h3 class="academia-name">
                            <i class="fas fa-tennis-ball academia-icon"></i> MELL Tennis
                        </h3>
                        <p class="academia-address">
                            <i class="fas fa-map-pin"></i> Em breve - Nova unidade
                        </p>
                        <p class="academia-phone">
                            <i class="fas fa-phone"></i> Informações em breve
                        </p>
                        <p class="academia-hours" style="color: #777; margin-top: 0.5rem;">
                            <i class="fas fa-clock"></i> Horários a definir
                        </p>
                    </div>
                </div>
            </section>
            
            <!-- Seção Treinamento -->
            <section class="treinamento-section">
                <h2 class="section-title">
                    <i class="fas fa-dumbbell"></i> Nosso Método de Treinamento
                </h2>
                
                <div class="treinamento-content">
                    <p>
                        Nossos treinamentos são desenvolvidos por profissionais certificados e adaptados para 
                        todas as idades e níveis, desde iniciantes até jogadores avançados.
                    </p>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;">
                        <div class="treinamento-item" style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
                            <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">
                                <i class="fas fa-cogs" style="color: #3498db;"></i> Técnica
                            </h4>
                            <p style="color: #666; font-size: 0.95rem;">
                                Fundamentos sólidos, golpes precisos e movimentos eficientes
                            </p>
                        </div>
                        
                        <div class="treinamento-item" style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
                            <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">
                                <i class="fas fa-chess" style="color: #3498db;"></i> Tática
                            </h4>
                            <p style="color: #666; font-size: 0.95rem;">
                                Estratégias de jogo, posicionamento e leitura do adversário
                            </p>
                        </div>
                        
                        <div class="treinamento-item" style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
                            <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">
                                <i class="fas fa-running" style="color: #3498db;"></i> Condicionamento
                            </h4>
                            <p style="color: #666; font-size: 0.95rem;">
                                Preparo físico específico para tênis, agilidade e resistência
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="container footer-content">
            <div class="footer-section">
                <h3>Tennis Academy</h3>
                <p>Excelência no ensino de tênis desde 2010. Formamos campeões dentro e fora das quadras.</p>
            </div>
            
            <div class="footer-section">
                <h3>Links Rápidos</h3>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/precos">Preços</a></li>
                    <li><a href="/cadastro">Cadastro</a></li>
                    <li><a href="/contato">Contato</a></li>
                </ul>
            </div>
            
            <div class="footer-section">
                <h3>Contato</h3>
                <p><i class="fas fa-phone"></i> (11) 98765-4321</p>
                <p><i class="fas fa-envelope"></i> contato@tennisacademy.com</p>
                <p><i class="fas fa-map-marker-alt"></i> São Paulo - SP</p>
            </div>
        </div>
        
        <div class="copyright">
            <p>&copy; 2024 Tennis Academy. Todos os direitos reservados.</p>
        </div>
    </footer>
    
    <!-- Scripts -->
    <script>
        // Script para destacar a seção ativa no menu
        document.addEventListener('DOMContentLoaded', function() {
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.nav-links a');
            
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentPath) {
                    link.classList.add('active');
                }
            });
            
            // Efeito nos balões de preço
            const priceBadges = document.querySelectorAll('.price-badge');
            priceBadges.forEach(badge => {
                badge.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.1)';
                    this.style.backgroundColor = 'rgba(128, 128, 128, 0.3)';
                });
                
                badge.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                    this.style.backgroundColor = 'rgba(128, 128, 128, 0.15)';
                });
            });
            
            // Animações de entrada
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, observerOptions);
            
            // Observar elementos para animação
            document.querySelectorAll('.aula-card, .academias-list, .treinamento-section').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(el);
            });
        });
    </script>
</body>
</html>
