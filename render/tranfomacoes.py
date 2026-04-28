import math

# =========================
# MATRIZES BASE
# =========================

def identidade():
    return [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

def translacao(tx, ty):
    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]

def escala(sx, sy):
    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]

def rotacao(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return [
        [ c, -s, 0],
        [ s,  c, 0],
        [ 0,  0, 1]
    ]

# =========================
# MULTIPLICAÇÃO DE MATRIZES
# =========================

def multiplica_matrizes(a, b):
    r = [[0]*3 for _ in range(3)]

    for i in range(3):
        for j in range(3):
            for k in range(3):
                r[i][j] += a[i][k] * b[k][j]

    return r

# =========================
# APLICAR EM PONTOS
# =========================

def aplica_transformacao(m, pontos):
    novos = []

    for x, y in pontos:
        v = [x, y, 1]

        x_novo = m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]
        y_novo = m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]

        novos.append((x_novo, y_novo))

    return novos

# =========================
# TRANSFORMAÇÃO COMPLETA
# =========================

def transformar_poligono(pontos, x, y, angulo, escala_val):
    # calcula centro
    cx = sum(p[0] for p in pontos) / len(pontos)
    cy = sum(p[1] for p in pontos) / len(pontos)

    # composição: T(-p) · R · S · T(p) · T(pos)
    m = identidade()

    m = multiplica_matrizes(translacao(-cx, -cy), m)
    m = multiplica_matrizes(rotacao(angulo), m)
    m = multiplica_matrizes(escala(escala_val, escala_val), m)
    m = multiplica_matrizes(translacao(cx, cy), m)
    m = multiplica_matrizes(translacao(x, y), m)

    return aplica_transformacao(m, pontos)