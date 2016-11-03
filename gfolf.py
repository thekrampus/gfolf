from sys import path

if __name__ == '__main__':
    path.append('lib')

    from src.game import Game
    g = Game()
    g.run()
