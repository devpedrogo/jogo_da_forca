# 🎯 Atividade Final - Mini Jogo via API

## 🎮 Jogo Escolhido: Jogo de Forca (Opção 1)

## 💻 Tecnologias e Frameworks Utilizados

* **Framework API:** FastAPI
* **Linguagem:** Python
* **Banco de Dados (Persistência):** SQLite (utilizando SQLAlchemy ORM)
* **Servidor:** Uvicorn

## 🖥️ Frontend

O frontend é uma página estática feita com HTML, CSS e JavaScript, localizada em `frontend/`. Não precisa de npm, instalação de pacotes nem etapa de build. Ele envia as requisições para a API em `http://127.0.0.1:8000`.

Com a API em execução, abra outro terminal na raiz do projeto e inicie o servidor local do frontend:

```powershell
py -m http.server 5501 --directory frontend
```

Mantenha os dois terminais abertos e acesse <http://127.0.0.1:5501> no navegador. Se a porta `5501` já estiver ocupada, encerre o processo anterior com `Ctrl+C` ou escolha outra porta livre no comando e na URL.

## 🛠️ Instruções Claras de Como Rodar o Projeto

### Pré-requisitos
* Python 3.8+ instalado.

### 1. Clonar o Repositório e Navegar para o Diretório
```bash
# Se estivesse em um repositório git
# git clone [seu-repositorio]
cd mini_jogo_forca
```

### 2. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 3. Executar o Servidor Uvicorn
```Bash
uvicorn api.main:app --reload
```
A API estará rodando em http://127.0.0.1:8000.
* Documentação da API: Acesse http://127.0.0.1:8000/docs para o Swagger UI interativo.

### Organização do backend

O backend usa camadas para separar responsabilidades:

* `api/routers`: endpoints HTTP e conversão de erros para respostas HTTP.
* `api/schemas`: contratos de entrada e saída da API.
* `api/services`: regras do jogo e casos de uso.
* `api/repositories`: consultas e persistência com SQLAlchemy.
* `api/models`: entidades/tabelas do banco.
* `api/core`: configuração e dependência da sessão do banco.

### 🔗 Exemplos de Requisições e Respostas
1. Criar Jogador
* Endpoint: POST /players
* Descrição: Cria um novo jogador para associar as partidas.
```
    Campo Exemplo (Body)
    name  "Pedro"
```

```
JSON
{
    "name": "Pedro"
}
```

##### Resposta (201 Created):
```
JSON
{
    "id": 1,
    "name": "Pedro"
}
```

### 2. Iniciar Nova Partida
* Endpoint: POST /hangman/start
* Descrição: Inicia uma nova partida de Forca para o jogador.
```
Campo      Exemplo (Body)
player_id   1
```

```
JSON
{
    "player_id": 1
}
```
#### Resposta (200 OK):

```
JSON
{
    "game_id": 101,
    "masked_word": "_______",
    "attempts_left": 6,
    "status": "IN_PROGRESS"
}
```
### 3. Tentar Letra (Guess)
* Endpoint: POST /hangman/guess
* Descrição: Envia uma letra para a partida (game_id).

```
Campo     Exemplo (Body)
game_id    101
letter     "A"
```

```
JSON
{
    "game_id": 101,
    "letter": "A"
}
```
#### Resposta (Acerto - 200 OK):
```
JSON
{
    "game_id": 101,
    "masked_word": "__A____",
    "attempts_left": 6,
    "status": "IN_PROGRESS",
    "hit": true
}
```
#### Resposta (Erro - 400 Bad Request - Jogada Inválida):
```
JSON
{
    "error": "A letra 'A' já foi tentada.",
    "code": 400
}
```

### 4. Placar de Jogadores
* Endpoint: GET /hangman/scoreboard
* Descrição: Retorna o ranking de vitórias e derrotas por jogador.

#### Resposta (200 OK):
```
JSON
[
    {
        "player_id": 1,
        "name": "Pedro",
        "wins": 3,
        "losses": 1,
        "total_games": 4
    }
]
```