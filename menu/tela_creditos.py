import pygame
from configs.config_jogo import LARGURA_TELA, ALTURA_TELA
from configs.config_menu import COR_TITULO, COR_BOTAO_BORDA
from render.preenchimento import scanline_fill


def tela_creditos(tela, relogio, tempo_total=10.0):

    # Renderiza a tela de créditos e retorna True quando termina.
    # tempo_total: duração da tela de créditos em segundos.

    tempo_decorrido = 0.0
    fonte_grande = pygame.font.SysFont(None, 48)
    fonte_normal = pygame.font.SysFont(None, 32)
    
    creditos_texto = [
        "PRÍNCIPE DORMINHOCO",
        "",
        "Desenvolvido com Pygame",
        "",
        "Equipe de Desenvolvimento:",
        "Gabryella Rodrigues",
        "Kalil Rodrigues",
        "Lucas Holanda",
        "",
        "Obrigado por jogar!",
        "",
        "FIM",
    ]
    
    while tempo_decorrido < tempo_total:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    return "menu"
        
        rect_bg = [(0, 0), (LARGURA_TELA, 0), (LARGURA_TELA, ALTURA_TELA), (0, ALTURA_TELA)]
        scanline_fill(tela, rect_bg, (10, 10, 10))
        
        # Opacidade baseada no tempo (fade in/out)
        progresso = tempo_decorrido / tempo_total
        if progresso < 0.1:
            alfa = int(255 * (progresso / 0.1))
        elif progresso > 0.9:
            alfa = int(255 * ((1.0 - progresso) / 0.1))
        else:
            alfa = 255
        
        # Renderizar créditos com movimento vertical
        y_offset = int(ALTURA_TELA - progresso * (ALTURA_TELA + 400))
        
        for i, texto in enumerate(creditos_texto):
            if texto.strip() == "":
                continue
            
            if texto == "PRÍNCIPE DORMINHOCO":
                surface = fonte_grande.render(texto, True, COR_TITULO)
            elif texto == "FIM":
                surface = fonte_grande.render(texto, True, COR_BOTAO_BORDA)
            else:
                surface = fonte_normal.render(texto, True, (200, 200, 200))
            
            surface.set_alpha(alfa)
            rect = surface.get_rect(center=(LARGURA_TELA // 2, y_offset + i * 60))
            tela.blit(surface, rect)
        
        pygame.display.flip()
        dt = relogio.tick(60) / 1000.0
        tempo_decorrido += dt
    
    return "menu"
