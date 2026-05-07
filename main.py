from menu.menu_principal import menu_principal
from jogo_principal import TestGameApp


def executar_jogo():
    app = TestGameApp()
    app.run()


def main():
    acao = menu_principal()
    if acao == "jogar":
        executar_jogo()


if __name__ == "__main__":
    main()
