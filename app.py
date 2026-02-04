// script.js - Funcionalidades JavaScript adicionais

// Suaviza rolagem para links âncora
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Formata números de telefone
function formatarTelefone(tel) {
    const apenasNumeros = tel.replace(/\D/g, '');
    if (apenasNumeros.length === 11) {
        return apenasNumeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    if (apenasNumeros.length === 10) {
        return apenasNumeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return tel;
}

// Atualiza todos os telefones na página
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.academia-phone').forEach(el => {
        el.textContent = formatarTelefone(el.textContent);
    });
});

// Contador de visitantes (simulação)
function atualizarContador() {
    const contador = localStorage.getItem('visitCount') || 0;
    const novoContador = parseInt(contador) + 1;
    localStorage.setItem('visitCount', novoContador);
    
    // Você pode exibir em algum lugar da página
    // document.getElementById('contador-visitas').textContent = novoContador;
}

// Verifica se é a primeira visita do dia
function primeiraVisitaHoje() {
    const ultimaVisita = localStorage.getItem('ultimaVisita');
    const hoje = new Date().toDateString();
    
    if (ultimaVisita !== hoje) {
        localStorage.setItem('ultimaVisita', hoje);
        return true;
    }
    return false;
}

// Inicialização
if (primeiraVisitaHoje()) {
    atualizarContador();
}

// Modo escuro/claro
const temaToggle = document.createElement('button');
temaToggle.innerHTML = '<i class="fas fa-moon"></i>';
temaToggle.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #2c3e50;
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
`;

document.body.appendChild(temaToggle);

temaToggle.addEventListener('click', function() {
    document.body.classList.toggle('modo-escuro');
    temaToggle.innerHTML = document.body.classList.contains('modo-escuro') 
        ? '<i class="fas fa-sun"></i>' 
        : '<i class="fas fa-moon"></i>';
});

// Adiciona CSS para modo escuro
const estiloModoEscuro = document.createElement('style');
estiloModoEscuro.textContent = `
    body.modo-escuro {
        --cor-primaria: #1a1a2e;
        --cor-secundaria: #3498db;
        --cor-fundo: #121212;
        --cor-texto: #e0e0e0;
        --cor-texto-claro: #b0b0b0;
        --cor-branco: #1e1e1e;
    }
    
    body.modo-escuro .aula-card,
    body.modo-escuro .academias-list,
    body.modo-escuro .treinamento-section,
    body.modo-escuro .treinamento-item {
        background: #2d2d2d;
        border-color: #404040;
    }
`;
document.head.appendChild(estiloModoEscuro);
