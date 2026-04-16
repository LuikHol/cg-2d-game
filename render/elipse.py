from render.pixel import setPixel

def desenhar_elipse(surface, xc, yc, rx, ry, color):
    x = 0
    y = ry

    rx2 = rx * rx
    ry2 = ry * ry

    p1 = ry2 - rx2 * ry + 0.25 * rx2

    # Região 1
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    while dx < dy:
        plot_ellipse(surface, xc, yc, x, y, color)

        if p1 < 0:
            x += 1
            dx = 2 * ry2 * x
            p1 += dx + ry2
        else:
            x += 1
            y -= 1
            dx = 2 * ry2 * x
            dy = 2 * rx2 * y
            p1 += dx - dy + ry2

    # Região 2
    p2 = (ry2 * (x + 0.5)**2) + (rx2 * (y - 1)**2) - (rx2 * ry2)

    while y >= 0:
        plot_ellipse(surface, xc, yc, x, y, color)

        if p2 > 0:
            y -= 1
            dy = 2 * rx2 * y
            p2 += rx2 - dy
        else:
            y -= 1
            x += 1
            dx = 2 * ry2 * x
            dy = 2 * rx2 * y
            p2 += dx - dy + rx2


def plot_ellipse(surface, xc, yc, x, y, color):
    setPixel(surface, xc + x, yc + y, color)
    setPixel(surface, xc - x, yc + y, color)
    setPixel(surface, xc + x, yc - y, color)
    setPixel(surface, xc - x, yc - y, color)