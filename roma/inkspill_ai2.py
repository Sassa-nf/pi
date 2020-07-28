ai_coord = (0, 0)
import random as rnd

def make_move(board, life):
    x0, y0 = ai_coord
    color = rnd.randint(0, len(board.palette_colors) - 1)
    print(f'best color:{color}')
    return color
