from render.pixel import setPixel

def bresenham(surface, x0, y0, x1, y1, color):
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = abs(y1 - y0)
    ystep = 1 if y0 < y1 else -1

    error = dx // 2
    y = y0

    for x in range(x0, x1 + 1):
        if steep:
            setPixel(surface, y, x, color)
        else:
            setPixel(surface, x, y, color)

        error -= dy
        if error < 0:
            y += ystep
            error += dx