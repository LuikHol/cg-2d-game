def foreground_img(caminho, x_base, y_base, w_base, h_base, escala=1.0):
    """Gera um item de foreground com escala proporcional.

    Parametros:
        x_base, y_base : posicao superior-esquerda do retangulo no espaco de mundo.
        w_base, h_base : largura e altura originais (escala=1.0).
        escala         : fator de zoom (1.1 = +10%, 0.9 = -10%).

    O rect resultante e centralizado no X e mantém a base (fundo) no mesmo y.
    """
    w = round(w_base * escala)
    h = round(h_base * escala)
    x = x_base - (w - w_base) // 2
    y = y_base - (h - h_base)
    return {"image_path": caminho, "rect": (x, y, w, h), "preserve_aspect": True}


def poligono_de_chao(pontos, cor_preenchimento, cor_borda):
    return {
        "polygon": pontos,
        "fill_color": cor_preenchimento,
        "border_color": cor_borda,
        "skip_on_background": True,
    }