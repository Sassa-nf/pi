depth_max = 5

def evaluate(board, player, depth):
    if depth >= depth_max or player.life <= 0 or player.score >= board.width * board.height:
        return None, player.score + player.life

    move_best, score_best = -1, -1
    for color in range(len(board.palette_colors)):
        if color == player.color:
            continue

        state = board.get_history_state()
        acquired = board.move(player.num, color)
        _, score = evaluate(board, player, depth + 1)
        if score > score_best:
            score_best = score
            move_best = color
        board.undo_to(state)

        if depth == 0:
            print(f'{color} -> {score}    ', end='')

    if depth == 0:
        print(' ')
    return move_best, score_best



def make_move(board, player):
    move_best, score_best = evaluate(board, player, depth=0)
    print(f'best move:{move_best} score:{score_best}\n')
    return move_best
