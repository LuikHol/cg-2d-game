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


def clip_polygon_sutherland_hodgman(pontos, xmin, ymin, xmax, ymax):
    # Recorta um polígono convexo contra um retângulo (janela) usando o algoritmo
    # Sutherland-Hodgman. Diferente do Cohen-Sutherland (que recorta linhas),
    # este opera sobre o polígono inteiro de uma vez, passando por 4 bordas em sequência.
    # Retorna um novo polígono (lista de pontos) já recortado dentro da janela.

    def inside(ponto, borda):
        # Testa se um ponto está do lado "dentro" de uma borda da janela.
        # Cada borda divide o plano em dois semiplanos: dentro e fora.
        x, y = ponto
        if borda == "left":
            return x >= xmin   # dentro = à direita da borda esquerda
        if borda == "right":
            return x <= xmax   # dentro = à esquerda da borda direita
        if borda == "top":
            return y >= ymin   # dentro = abaixo da borda de cima (y cresce pra baixo)
        return y <= ymax       # dentro = acima da borda de baixo

    def intersect(p1, p2, borda):
        # Calcula o ponto exato onde a aresta (p1 -> p2) cruza a borda da janela.
        # Usa interpolação paramétrica: t indica "quanto" da aresta percorrer até a borda.
        x1, y1 = p1
        x2, y2 = p2

        if borda in ("left", "right"):
            # Borda vertical: x é fixo, calcula y.
            x_borda = xmin if borda == "left" else xmax
            if x2 == x1:
                # Aresta paralela à borda: evita divisão por zero, retorna ponto na borda.
                return x_borda, y1
            t = (x_borda - x1) / (x2 - x1)   # fração do caminho de p1 até p2
            return x_borda, y1 + t * (y2 - y1)

        # Borda horizontal: y é fixo, calcula x.
        y_borda = ymin if borda == "top" else ymax
        if y2 == y1:
            # Aresta paralela à borda: evita divisão por zero.
            return x1, y_borda
        t = (y_borda - y1) / (y2 - y1)        # fração do caminho de p1 até p2
        return x1 + t * (x2 - x1), y_borda

    if not pontos:
        return []

    # Começa com o polígono original e passa por cada borda da janela uma vez.
    # A cada passagem, o polígono é recortado contra aquela borda e o resultado
    # vira entrada da próxima passagem.
    saida = pontos[:]
    for borda in ["left", "right", "top", "bottom"]:
        entrada = saida   # resultado da passagem anterior vira a entrada desta
        saida = []
        if not entrada:
            break          # polígono foi totalmente eliminado, para cedo

        # s = ponto anterior (começa pelo último para fechar o polígono)
        s = entrada[-1]
        for e in entrada:
            # Regra de Sutherland-Hodgman para cada aresta s -> e:
            if inside(e, borda):
                if not inside(s, borda):
                    # s estava fora, e está dentro: entra na janela.
                    # Adiciona o ponto de cruzamento antes de e.
                    saida.append(intersect(s, e, borda))
                # e está dentro: sempre adiciona.
                saida.append(e)
            elif inside(s, borda):
                # s estava dentro, e está fora: sai da janela.
                # Adiciona só o ponto de cruzamento (e fica de fora).
                saida.append(intersect(s, e, borda))
            # s fora e e fora: não adiciona nada.
            s = e   # avança o ponto anterior

    # Converte coordenadas float de volta para inteiros de pixel.
    return [(int(round(x)), int(round(y))) for x, y in saida]