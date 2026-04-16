# Codigos de regiao usados para classificar onde um ponto esta em relacao a janela.
# Cada constante representa um bit: pode-se combinar com | para indicar dois lados ao mesmo tempo.
INSIDE = 0   # dentro da janela
LEFT   = 1   # a esquerda
RIGHT  = 2   # a direita
BOTTOM = 4   # abaixo
TOP    = 8   # acima

def compute_code(x, y, xmin, ymin, xmax, ymax):
    # Começa assumindo que o ponto esta dentro.
    code = INSIDE

    # Verifica o eixo horizontal.
    if x < xmin:
        code |= LEFT           # fora pela esquerda
    elif x > xmax:
        code |= RIGHT          # fora pela direita

    # Verifica o eixo vertical (y cresce para baixo na tela).
    if y < ymin:
        code |= TOP            # acima da janela
    elif y > ymax:
        code |= BOTTOM         # abaixo da janela

    return code


def cohen_sutherland(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    # Calcula o codigo de regiao para cada ponta da linha.
    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    accept = False

    while True:
        if code1 == 0 and code2 == 0:
            # Os dois pontos estao dentro: aceita a linha inteira.
            accept = True
            break

        elif (code1 & code2) != 0:
            # Os dois pontos compartilham uma regiao externa: linha totalmente fora.
            break

        else:
            # A linha cruza a janela: precisa ser cortada.

            # Escolhe a ponta que esta fora para cortar primeiro.
            if code1 != 0:
                code_out = code1
            else:
                code_out = code2

            # Calcula o ponto de intersecao com a borda correspondente.
            if code_out & TOP:
                # Cruza a borda do topo: interpola x para y = ymin.
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin

            elif code_out & BOTTOM:
                # Cruza a borda de baixo: interpola x para y = ymax.
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax

            elif code_out & RIGHT:
                # Cruza a borda direita: interpola y para x = xmax.
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax

            elif code_out & LEFT:
                # Cruza a borda esquerda: interpola y para x = xmin.
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            # Substitui a ponta que estava fora pelo novo ponto cortado.
            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        return int(x1), int(y1), int(x2), int(y2)
    else:
        return None