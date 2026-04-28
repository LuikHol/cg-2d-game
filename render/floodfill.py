from render.pixel import setPixel


def flood_fill(surface, x, y, new_color, border_color):
    # A pilha guarda os pixels que ainda precisam ser analisados.
    stack = [(x, y)]

    while stack:
        # Remove o ultimo pixel adicionado para processar agora.
        x, y = stack.pop()

        # Ignora pixels que estejam fora dos limites da tela.
        if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
            continue

        # Le a cor atual do pixel; [:3] pega apenas RGB e ignora alpha.
        current = surface.get_at((x, y))[:3]

        # Para ao encontrar a borda ou uma area que ja foi preenchida.
        if current == border_color or current == new_color:
            continue

        # Pinta o pixel atual com a nova cor.
        setPixel(surface, x, y, new_color)

        # Adiciona os 4 vizinhos para continuar o preenchimento.
        stack.append((x+1, y))
        stack.append((x-1, y))
        stack.append((x, y+1))
        stack.append((x, y-1))