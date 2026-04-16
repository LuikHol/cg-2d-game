def world_to_viewport(x, y, win, vp):
    # Desempacota os limites da janela no mundo e da viewport na tela.
    wxmin, wymin, wxmax, wymax = win
    vxmin, vymin, vxmax, vymax = vp

    # Calcula o fator de escala: quantos pixels de tela correspondem a uma unidade do mundo.
    sx = (vxmax - vxmin) / (wxmax - wxmin)
    sy = (vymax - vymin) / (wymax - wymin)

    # Aplica a transformacao: move a origem para a viewport e escala o ponto.
    xv = vxmin + (x - wxmin) * sx
    yv = vymin + (y - wymin) * sy

    # Retorna as coordenadas ja convertidas para inteiro (pixels).
    return int(xv), int(yv)

def transformar_pontos(pontos, win, vp):
    novos = []  # lista que vai receber os pontos ja transformados
    for x, y in pontos:
        # Converte cada ponto do espaco do mundo para coordenadas de tela.
        xv, yv = world_to_viewport(x, y, win, vp)
        novos.append((xv, yv))
    return novos