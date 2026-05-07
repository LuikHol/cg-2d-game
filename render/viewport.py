def mundo_para_viewport(x, y, win, vp):
    wxmin, wymin, wxmax, wymax = win
    vxmin, vymin, vxmax, vymax = vp

    sx = (vxmax - vxmin) / (wxmax - wxmin)
    sy = (vymax - vymin) / (wymax - wymin)

    xv = vxmin + (x - wxmin) * sx
    yv = vymin + (y - wymin) * sy

    return int(xv), int(yv)

def transformar_pontos(pontos, win, vp):
    novos = []
    for x, y in pontos:
        xv, yv = mundo_para_viewport(x, y, win, vp)
        novos.append((xv, yv))
    return novos


def atualizar_camera_player_follow(player_x, player_y, camera_bounds, camera_size):
    """Centraliza a camera no jogador, mantendo tamanho fixo da janela de mundo."""
    camera_w, camera_h = camera_size

    cx_min = player_x - (camera_w / 2)
    cy_min = player_y - (camera_h / 2)
    cx_max = cx_min + camera_w
    cy_max = cy_min + camera_h

    if camera_bounds:
        bound_xmin, bound_ymin, bound_xmax, bound_ymax = camera_bounds

        if cx_min < bound_xmin:
            cx_min = bound_xmin
            cx_max = cx_min + camera_w
        elif cx_max > bound_xmax:
            cx_max = bound_xmax
            cx_min = cx_max - camera_w

        if cy_min < bound_ymin:
            cy_min = bound_ymin
            cy_max = cy_min + camera_h
        elif cy_max > bound_ymax:
            cy_max = bound_ymax
            cy_min = cy_max - camera_h

    return (cx_min, cy_min, cx_max, cy_max)