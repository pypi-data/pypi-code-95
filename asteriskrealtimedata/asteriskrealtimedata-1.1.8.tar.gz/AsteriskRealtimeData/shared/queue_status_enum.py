from enum import Enum


class QueueStatus(Enum):
    DESCONOCIDO = 0
    SINUSO = 1
    HABLANDO = 2
    OCUPADO = 3
    INVALIDO = 4
    INDISPONIBLE = 5
    RINGING = 6
    RINGINUSE = 7
    ENESPERA = 8
    CORTANDO = 9
