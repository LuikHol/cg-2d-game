from render.pixel import setPixel

def scanline_texture(surface, pontos, textura):
    # Coleta os valores de y para saber a altura total do poligono.
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))

    # Tamanho real da imagem de textura em pixels.
    largura_tex = textura.get_width()
    altura_tex = textura.get_height()

    # Quantidade de vertices do poligono.
    n = len(pontos)

    # Varre cada linha horizontal entre o topo e a base do poligono.
    for y in range(y_min, y_max):
        intersecoes = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i+1) % n]

            # Ignora arestas horizontais.
            if y0 == y1:
                continue

            if y0 > y1:
                # Garante que a aresta va sempre de cima para baixo.
                x0, y0, x1, y1 = x1, y1, x0, y0

            # Usa apenas arestas que cruzam a linha atual.
            if y < y0 or y >= y1:
                continue

            # Calcula o x exato onde a aresta cruza a scanline.
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes.append(x)

        # Ordena os cruzamentos da esquerda para a direita.
        intersecoes.sort()

        # Preenche entre pares: o primeiro e a entrada, o segundo e a saida do poligono.
        for i in range(0, len(intersecoes), 2):
            if i + 1 < len(intersecoes):
                x_ini = int(intersecoes[i])
                x_fim = int(intersecoes[i+1])

                for x in range(x_ini, x_fim + 1):

                    # u: posicao relativa horizontal dentro do trecho (0 = esquerda, 1 = direita).
                    u = (x - x_ini) / max(1, (x_fim - x_ini))
                    # v: posicao relativa vertical dentro do poligono (0 = topo, 1 = base).
                    v = (y - y_min) / max(1, (y_max - y_min))

                    # Converte u e v para coordenadas reais de pixel na imagem.
                    tex_x = int(u * (largura_tex - 1))
                    tex_y = int(v * (altura_tex - 1))

                    # Le a cor da textura naquela posicao.
                    cor = textura.get_at((tex_x, tex_y))

                    # Pinta o pixel do poligono com a cor lida da textura.
                    setPixel(surface, x, y, cor)