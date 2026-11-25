// script.js

const API_BASE_URL = 'http://127.0.0.1:8000';

// Estado global da aplicação
let currentPlayerId = null;
let currentGameId = null;
let currentWord = '';
let currentTriedLetters = '';
let currentAttemptsLeft = 6;

// ==========================================================
// FUNÇÕES DE UTILIDADE E RENDERIZAÇÃO
// ==========================================================

// Mapas ASCII para o boneco da forca (6 erros -> 0 tentativas)
const HANGMAN_FIGURES = [
    `
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========
    `, // 0 tentativas restantes (Game Over)
    `
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========
    `, // 1 tentativa restante (Perna Direita)
    `
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========
    `, // 2 tentativas restantes (Perna Esquerda)
    `
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
    `, // 3 tentativas restantes (Braço Direito)
    `
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
    `, // 4 tentativas restantes (Braço Esquerdo)
    `
  +---+
  |   |
  O   |
      |
      |
      |
=========
    `, // 5 tentativas restantes (Corpo)
    `
  +---+
  |   |
      |
      |
      |
      |
=========
    `, // 6 tentativas restantes (Início)
];

function updateGameDisplay(gameStatus, message = '') {
    currentWord = gameStatus.masked_word;
    currentAttemptsLeft = gameStatus.attempts_left;

    // Atualiza a palavra e o número de tentativas
    document.getElementById('masked-word').textContent = currentWord;
    document.getElementById('attempts-left').textContent = currentAttemptsLeft;
    document.getElementById('game-id-display').textContent = gameStatus.game_id;

    // Mapeia tentativas restantes para o índice correto do HANGMAN_FIGURES
    const figureIndex = Math.min(6, Math.max(0, currentAttemptsLeft));
    document.getElementById('figure-display').textContent = HANGMAN_FIGURES[figureIndex];

    // ----------------------------------------------------
    // LÓGICA DE EXIBIÇÃO DAS LETRAS TENTADAS (CORRIGIDA)
    // ----------------------------------------------------
    const lettersFromBackend = gameStatus.guessed_letters; 

    // Se a string do backend existir E não for uma string vazia (length > 0), use-a.
    // Caso contrário, mostre 'Nenhuma'.
    const triedLettersText = (lettersFromBackend && lettersFromBackend.length > 0)
                             ? lettersFromBackend 
                             : 'Nenhuma';
        
    document.getElementById('tried-letters').textContent = triedLettersText;
    // ----------------------------------------------------

    // Exibe a mensagem de status (WIN, LOSE, IN_PROGRESS)
    const statusEl = document.getElementById('message');
    statusEl.textContent = message;
    statusEl.className = 'status-message';
    document.getElementById('guess-input').value = '';

    // Lógica de Fim de Jogo
    if (gameStatus.status === 'WIN') {
        statusEl.textContent = `🎉 PARABÉNS! Você VENCEU! A palavra era: ${gameStatus.word || currentWord.replace(/_/g, '')}`;
        document.getElementById('guess-control').style.display = 'none';
        document.getElementById('start-button').disabled = false; // Permite iniciar novo jogo
    } else if (gameStatus.status === 'LOSE') {
        statusEl.textContent = `😭 GAME OVER! Você PERDEU! A palavra secreta era: ${gameStatus.word || 'Não revelada (verifique o console)'}`;
        document.getElementById('guess-control').style.display = 'none';
        document.getElementById('start-button').disabled = false; // Permite iniciar novo jogo
    } else {
        document.getElementById('guess-control').style.display = 'flex';
    }
}


function displayMessage(message, isError = false) {
    const statusEl = document.getElementById('player-status');
    statusEl.textContent = message;
    statusEl.style.color = isError ? 'red' : 'green';
}


// ==========================================================
// FUNÇÕES DE CHAMADA À API (Endpoints)
// ==========================================================

// 1. POST /players (Lógica Buscar ou Criar)
async function createOrLoadPlayer() {
    const playerName = document.getElementById('player-name').value.trim();
    if (!playerName) {
        displayMessage('Por favor, digite seu nome.', true);
        return;
    }

    let player;

    // 1. TENTATIVA: Tentar buscar o jogador existente pelo nome (GET)
    try {
        const response = await fetch(`${API_BASE_URL}/players/${playerName}`);
        
        if (response.ok) {
            // Sucesso: Jogador encontrado!
            player = await response.json();
            displayMessage(`Bem-vindo de volta, ${player.name}! ID: ${player.id}`);
            
        } else if (response.status === 404) {
            // 404: Jogador não encontrado, prosseguir para a criação (POST)
            console.log("Jogador não encontrado, tentando criar novo...");
            
            // 2. TENTATIVA: Criar o novo jogador (POST)
            const createResponse = await fetch(`${API_BASE_URL}/players`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: playerName }),
            });

            if (!createResponse.ok) {
                // Erro na criação (ex: nome inválido/duplicado)
                const errorData = await createResponse.json();
                // Mostra a mensagem de erro específica do backend (IntegrityError)
                displayMessage(`Erro ao criar jogador: ${errorData.detail.error || 'Falha de validação.'}`, true);
                return;
            }
            
            player = await createResponse.json();
            displayMessage(`Bem-vindo, ${player.name}! ID: ${player.id}`);

        } else {
            // Outro erro HTTP que não seja 404 (ex: 500)
            displayMessage(`Erro ao buscar jogador: ${response.status}`, true);
            return;
        }

    } catch (error) {
        // Erro de conexão de rede real (CORS/servidor fora do ar)
        console.error('Erro de conexão:', error);
        displayMessage('Erro de conexão com o backend FastAPI.', true);
        return;
    }

    // Lógica de sucesso (Executada se o jogador foi encontrado ou criado)
    currentPlayerId = player.id;
    document.getElementById('player-name').value = player.name;
    document.getElementById('start-button').disabled = false;
    // O elemento playerInfo não existe no HTML que forneci, então use player-status:
    document.getElementById('player-status').innerHTML = `Bem-vindo, ${player.name}! ID: ${player.id}.`;
    
    // Atualiza o placar após o login
    loadScoreboard(); 
}

// 2. POST /hangman/start
async function startGame() {
    if (!currentPlayerId) {
        displayMessage('Crie ou carregue um jogador primeiro.', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/hangman/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: currentPlayerId })
        });

        if (response.ok) {
            const gameStatus = await response.json();
            currentGameId = gameStatus.game_id;
            document.getElementById('game-empty').style.display = 'none';
            document.getElementById('game-content').style.display = 'grid';
            document.getElementById('start-button').disabled = true;
            document.getElementById('guess-control').style.display = 'flex';
            updateGameDisplay(gameStatus, 'Novo jogo iniciado!');
        } else {
            const errorData = await response.json();
            displayMessage(`Erro ao iniciar jogo: ${errorData.detail.error}`, true);
        }
    } catch (error) {
        console.error('Erro ao iniciar jogo:', error);
        displayMessage('Erro de conexão com o backend FastAPI.', true);
    }
}

// 3. POST /hangman/guess
async function makeGuess() {
    const letter = document.getElementById('guess-input').value.trim().toUpperCase();
    if (!letter || letter.length !== 1 || !letter.match(/[A-Z]/)) {
        displayMessage('Digite apenas uma letra válida.', true);
        return;
    }
    if (!currentGameId) {
        displayMessage('Inicie um novo jogo primeiro.', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/hangman/guess`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: currentGameId, letter: letter })
        });

        const gameStatus = await response.json();

        if (response.ok) {
            const message = gameStatus.hit ? `ACERTOU! A letra ${letter} está na palavra.` : `ERROU! A letra ${letter} não está na palavra.`;
            updateGameDisplay(gameStatus, message);
        } else {
            // Se houver erro (400 - letra repetida, ou jogo terminado), 
            // exibe a mensagem de erro, e depois tenta recarregar o estado
            
            if (gameStatus.detail && gameStatus.detail.error) {
                 displayMessage(`Erro na jogada: ${gameStatus.detail.error}`, true);
            } else {
                 displayMessage(`Erro na jogada (Status: ${response.status})`, true);
            }
            
            // Recarrega o status para ter certeza que a tela está sincronizada
            // (ex: para mostrar que o jogo já terminou)
            loadGameStatus();
        }

    } catch (error) {
        console.error('Erro ao fazer jogada:', error);
        displayMessage('Erro de conexão com o backend FastAPI.', true);
    }
}

// 4. GET /hangman/status/{game_id}
async function loadGameStatus() {
    if (!currentGameId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/hangman/status/${currentGameId}`);

        if (response.ok) {
            const gameStatus = await response.json();
            updateGameDisplay(gameStatus, `Jogo ID ${currentGameId} carregado.`);
        }
    } catch (error) {
        console.error('Erro ao carregar status do jogo:', error);
    }
}

// 5. GET /hangman/scoreboard
async function loadScoreboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/hangman/scoreboard`);
        const scoreboard = await response.json();

        const listEl = document.getElementById('scoreboard-list');
        listEl.innerHTML = ''; // Limpa a lista

        if (scoreboard.length === 0) {
            listEl.innerHTML = '<li>Nenhum placar registrado ainda.</li>';
            return;
        }

        scoreboard.forEach(entry => {
            const listItem = document.createElement('li');
            listItem.textContent = `[ID: ${entry.player_id}] ${entry.name} - Vitórias: ${entry.wins} / Derrotas: ${entry.losses} (Total: ${entry.total_games})`;
            listEl.appendChild(listItem);
        });

    } catch (error) {
        console.error('Erro ao carregar placar:', error);
        document.getElementById('scoreboard-list').innerHTML = '<li>Erro ao carregar placar. Verifique o console.</li>';
    }
}

// Carregar placar ao carregar a página
document.addEventListener('DOMContentLoaded', loadScoreboard);