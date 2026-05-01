from world.salas import criar_biblioteca, criar_corredor, criar_sala1, criar_sala2


def construir_salas():
    return {
        "sala_1": criar_sala1(),
        "corredor": criar_corredor(),
        "sala_2": criar_sala2(),
        "biblioteca": criar_biblioteca(),
    }