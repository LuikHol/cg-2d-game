import math
from render.utils_geometrias import centroide_poligono

# =========================
# MATRIZES BASE
# =========================

def identidade():
    # Matriz identidade 3x3 para coordenadas homogeneas.
    # Nao altera o ponto quando aplicada: p' = I * p.
    return [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

def translacao(tx, ty):
    # Move pontos em tx no eixo X e ty no eixo Y.
    # Em homogeneas, a translacao vai na ultima coluna.
    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]

def escala(sx, sy):
    # Escala independente por eixo em torno da origem (0, 0).
    # Valores > 1 aumentam, entre 0 e 1 reduzem.
    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]

def rotacao(theta):
    # Rotacao em radianos ao redor da origem, sentido anti-horario.
    # Forma padrao da matriz de rotacao 2D.
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
    # Produto matricial 3x3: r = a * b.
    # A ordem importa: em transformacoes geometricas, trocar a ordem muda o resultado.
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
    # Aplica a matriz m em cada ponto (x, y) assumindo z=1 em homogeneas.
    # Isso permite combinar translacao, escala e rotacao na mesma estrutura.
    novos = []

    for x, y in pontos:
        v = [x, y, 1]

        # Multiplicacao manual da linha da matriz pelo vetor do ponto.
        x_novo = m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]
        y_novo = m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]

        novos.append((x_novo, y_novo))

    return novos

# =========================
# TRANSFORMAÇÃO COMPLETA
# =========================

def transformar_poligono(pontos, x, y, angulo, escala_val):
    # Calcula centro geometrico (media dos vertices) para usar como pivô.
    # Assim a rotacao/escala acontecem "no proprio objeto", e nao no (0, 0) global.
    cx, cy = centroide_poligono(pontos)

    # Composicao das transformacoes (aplicadas da direita para a esquerda no ponto):
    # 1) Leva o pivô para a origem: T(-c)
    # 2) Rotaciona: R
    # 3) Escala: S
    # 4) Devolve para a posicao original do pivô: T(c)
    # 5) Move o objeto no mundo: T(x, y)
    m = identidade()

    # Cada linha pre-multiplica a matriz acumulada para manter a ordem acima.
    m = multiplica_matrizes(translacao(-cx, -cy), m)
    m = multiplica_matrizes(rotacao(angulo), m)
    m = multiplica_matrizes(escala(escala_val, escala_val), m)
    m = multiplica_matrizes(translacao(cx, cy), m)
    m = multiplica_matrizes(translacao(x, y), m)

    return aplica_transformacao(m, pontos)