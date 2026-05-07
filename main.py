from menu.menu_principal import menu_principal
from jogo_principal import TestGameApp


def executar_jogo():
    app = TestGameApp()
    app.run()


def main():
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
