class PlayerNotFound(Exception):
    """Indica que o jogador solicitado não existe."""

    pass


class PlayerAlreadyExists(Exception):
    """Indica que o nome do jogador já está cadastrado."""

    pass


class GameNotFound(Exception):
    """Indica que a partida solicitada não existe."""

    pass


class GameAlreadyFinished(Exception):
    """Indica que uma tentativa foi enviada após o fim da partida."""

    pass


class InvalidGuess(Exception):
    """Indica que a tentativa não atende às regras do jogo."""

    pass
