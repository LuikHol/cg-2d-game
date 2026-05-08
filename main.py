
from render.splash_screen import exibir_splash_screen
from configs.config_menu import LARGURA, ALTURA
from menu.menu_principal import menu_principal
from jogo_principal import TestGameApp


def executar_jogo():
    app = TestGameApp()
    app.run()


def main():
    if not exibir_splash_screen(LARGURA, ALTURA, duracao=3.2):
        return

    acao = menu_principal()
    if acao == "jogar":
        executar_jogo()
    while True:
        acao = menu_principal()
        if acao == "jogar":
            try:
                executar_jogo()
            except SystemExit:
                pass
        else:
            break


if __name__ == "__main__":
    main()
