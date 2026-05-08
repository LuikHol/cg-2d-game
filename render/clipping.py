from configs.config_clipping import ABAIXO, ACIMA, DENTRO, DIREITA, ESQUERDA

# Codigos de regiao usados para classificar onde um ponto esta em relacao a janela.
# Cada constante representa um bit: pode-se combinar com | para indicar dois lados ao mesmo tempo.

def computar_code(x, y, xmin, ymin, xmax, ymax):
    code = DENTRO

    if x < xmin:
        code |= ESQUERDA # fora pela esquerda
    elif x > xmax:
        code |= DIREITA # fora pela direita

    if y < ymin:
        code |= ACIMA # acima da janela
    elif y > ymax:
        code |= ABAIXO # abaixo da janela

    return code


def cohen_sutherland(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    code1 = computar_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = computar_code(x2, y2, xmin, ymin, xmax, ymax)

    accept = False

    while True:
        if code1 == 0 and code2 == 0:
            accept = True
            break

        elif (code1 & code2) != 0:
            break

        else:
            if code1 != 0:
                code_out = code1
            else:
                code_out = code2

            if code_out & ACIMA:
                # Cruza a borda do topo: interpola x para y = ymin.
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin

            elif code_out & ABAIXO:
                # Cruza a borda de baixo: interpola x para y = ymax.
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax

            elif code_out & DIREITA:
                # Cruza a borda direita: interpola y para x = xmax.
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax

            elif code_out & ESQUERDA:
                # Cruza a borda esquerda: interpola y para x = xmin.
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            # Substitui a ponta que estava fora pelo novo ponto cortado.
            if code_out == code1:
                x1, y1 = x, y
                code1 = computar_code(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = computar_code(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        return int(x1), int(y1), int(x2), int(y2)
    else:
        return None

def clip_polygon_com_cohen_sutherland(pontos, xmin, ymin, xmax, ymax):
    """Clippa um polígono usando Cohen-Sutherland em cada aresta.

    Percorre cada aresta (p_i -> p_{i+1}) do polígono, aplica o algoritmo
    Cohen-Sutherland para recortá-la contra o retângulo [xmin,xmax]x[ymin,ymax]
    e monta o polígono resultante com os segmentos visíveis.
    """
    if not pontos:
        return []

    saida = []
    n = len(pontos)
    for i in range(n):
        x1, y1 = pontos[i]
        x2, y2 = pontos[(i + 1) % n]
        resultado = cohen_sutherland(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
        if resultado is None:
            # Aresta totalmente fora da janela: descarta.
            continue
        cx1, cy1, cx2, cy2 = resultado
        # Evita duplicar o ponto inicial caso já tenha sido adicionado pela aresta anterior.
        if not saida or saida[-1] != (cx1, cy1):
            saida.append((cx1, cy1))
        saida.append((cx2, cy2))

    return saida