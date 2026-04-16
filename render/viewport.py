def world_to_viewport(x, y, win, vp):
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
        xv, yv = world_to_viewport(x, y, win, vp)
        novos.append((xv, yv))
    return novos