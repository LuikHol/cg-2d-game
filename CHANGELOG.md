# Changelog

## Refatoracao de Concisao e Modularidade

Esta versao nao muda a proposta do jogo. O que mudou foi a organizacao interna do codigo: menos repeticao, menos arquivos espalhados e pontos centrais mais claros para manter o projeto.

O comportamento esperado continua o mesmo: o menu abre por `main.py`, o jogo inicia normalmente, e os modulos continuam fazendo o mesmo trabalho de antes, so que com menos duplicacao.

## O que mudou

### Geometria foi centralizada

Antes, calculos como centroide de poligono, bounds e pontos de elipse apareciam repetidos em varios lugares.

Agora isso fica concentrado em `render/geometry_utils.py`.

Funcoes centralizadas:

1. `polygon_centroid`
2. `polygon_bounds`
3. `ellipse_points`

Impacto:

1. `render/transformacoes.py`, `objetos/polygon_object.py` e `objetos/objeto_interagivel.py` deixaram de recalcular o centro manualmente.
2. `render/iluminacao.py` e `objetos/player_object.py` passaram a usar a mesma logica para gerar elipses.
3. A area interativa de objetos agora usa uma funcao unica para bounds.

Na pratica, isso reduz divergencia entre modulos e deixa os calculos mais consistentes.

### O scanline agora tem um nucleo unico

Antes, o preenchimento solido e o preenchimento com textura repetiam quase toda a mesma logica de varredura.

Agora a parte comum foi isolada em `render/scanline_core.py`, com a funcao `iter_scanline_spans`.

Na pratica:

1. o algoritmo base de varredura existe em um unico lugar
2. os modulos de preenchimento so cuidam do que fazer com cada faixa horizontal

Isso deixa o codigo mais curto e mais facil de ajustar no futuro.

### Os modulos de preenchimento foram unidos

Antes, o projeto separava isso em:

1. `render/scanline.py`
2. `render/textura.py`

Agora tudo foi agrupado em `render/preenchimento.py`.

Esse arquivo passou a concentrar:

1. `scanline_fill`
2. `scanline_texture`

Arquivos atualizados para usar o novo modulo:

1. `menu/main_menu.py`
2. `menu/inventory_hud.py`
3. `objetos/interaction_manager.py`
4. `objetos/player_object.py`
5. `objetos/polygon_object.py`
6. `render/iluminacao.py`
7. `render/sala_renderer.py`

Arquivos removidos:

1. `render/scanline.py`
2. `render/textura.py`

Na pratica, o projeto continua preenchendo poligonos do mesmo jeito, mas agora essa responsabilidade ficou reunida em um unico lugar.

### O componente interativo foi incorporado ao objeto interativo

Antes, a logica estava separada entre:

1. `objetos/componente_interagivel.py`
2. `objetos/objeto_interagivel.py`

Agora `ComponenteInteragivel` foi movido para `objetos/objeto_interagivel.py`.

O funcionamento nao mudou: `ObjetoInterativo` continua criando `self.component` como antes.

Arquivo removido:

1. `objetos/componente_interagivel.py`

Na pratica, isso reduz um arquivo que existia separado mesmo tendo uso muito acoplado ao objeto principal.

### As primitivas de rasterizacao foram agrupadas

Antes, as primitivas estavam espalhadas em varios arquivos:

1. `render/linha.py`
2. `render/circulo.py`
3. `render/elipse.py`
4. `render/floodfill.py`

Agora tudo foi reunido em `render/primitivas.py`.

Esse modulo passou a concentrar:

1. `bresenham`
2. `desenhar_circulo`
3. `desenhar_elipse`
4. `flood_fill`

Mudanca associada:

1. `render/poligono.py` agora importa `bresenham` de `render/primitivas.py`

Arquivos removidos:

1. `render/linha.py`
2. `render/circulo.py`
3. `render/elipse.py`
4. `render/floodfill.py`

Na pratica, o codigo de rasterizacao ficou mais facil de localizar e manter.

### Pequenos ajustes internos

Nao houve mudanca funcional planejada no gameplay, mas algumas implementacoes foram alinhadas:

1. sombra do player e iluminacao agora usam a mesma base para gerar elipses
2. centroides e bounds deixaram de ser recalculados manualmente em varios pontos
3. a parte de preenchimento agora compartilha a mesma logica de varredura

O efeito disso e mais consistencia e menos chance de um modulo evoluir diferente do outro sem necessidade.

## Arquivos novos

1. `render/geometry_utils.py`
2. `render/scanline_core.py`
3. `render/preenchimento.py`
4. `render/primitivas.py`

## Arquivos removidos

1. `objetos/componente_interagivel.py`
2. `render/scanline.py`
3. `render/textura.py`
4. `render/linha.py`
5. `render/circulo.py`
6. `render/elipse.py`
7. `render/floodfill.py`
8. `configs/config.py`