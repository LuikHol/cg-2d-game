from render.pixel import setPixel

def desenhar_circulo(surface, xc, yc, r, color):
    x = 0
    y = r
    d = 1 - r

    def plot(x, y):
        setPixel(surface, xc + x, yc + y, color)
        setPixel(surface, xc - x, yc + y, color)
        setPixel(surface, xc + x, yc - y, color)
        setPixel(surface, xc - x, yc - y, color)
        setPixel(surface, xc + y, yc + x, color)
        setPixel(surface, xc - y, yc + x, color)
        setPixel(surface, xc + y, yc - x, color)
        setPixel(surface, xc - y, yc - x, color)

    while x <= y:
        plot(x, y)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1