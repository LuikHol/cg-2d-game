from mundo.salas import criar_biblioteca, criar_corredor, criar_creditos, criar_quarto_dia, criar_quarto_rainha, criar_sala1, criar_sala2


def construir_salas():
    return {
        "sala_1": criar_sala1(),
        "corredor": criar_corredor(),
        "sala_2": criar_sala2(),
        "quarto_dia": criar_quarto_dia(),
        "creditos": criar_creditos(),
        "biblioteca": criar_biblioteca(),
        "quarto_rainha": criar_quarto_rainha(),
    }