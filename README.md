# 🎯 Atividade Final - Mini Jogo via API

## 🎮 Jogo Escolhido: Jogo de Forca (Opção 1)

## 💻 Tecnologias e Frameworks Utilizados

* **Framework API:** FastAPI
* **Linguagem:** Python
* **Banco de Dados (Persistência):** SQLite (utilizando SQLAlchemy ORM)
* **Servidor:** Uvicorn

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
uvicorn app.main:app --reload
```
A API estará rodando em http://127.0.0.1:8000.
* Documentação da API: Acesse http://127.0.0.1:8000/docs para o Swagger UI interativo.

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