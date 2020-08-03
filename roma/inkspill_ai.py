import random as rnd

depth_max = 6


def set_depth(depth):
    global depth_max
    depth_max = depth


def get_depth():
    return depth_max


def evaluate(board, depth):
    if depth >= depth_max:
        move = [None] * len(board.player)
        score = [0] * len(board.player)
        for num in range(1, len(board.player)):
            player = board.player[num]
            score[num] = player.area + player.life + len(player.border) * 0.5
            if len(player.border) == 0:
                score[num] += 1000
        return move, score

    player = board.current_player
    player_num = board.current_player_num
    f_dummy = False
    if player.life <= 0 or len(player.border) == 0:
        f_dummy = True
        color_lst = [player.color]
    else:
        color_lst = range(len(board.palette_colors))

    move_best = [None] * len(board.player)
    score_best = [-1] * len(board.player)
    for color in color_lst:
        if color == board.current_player.color and f_dummy == False:
            continue

        state = board.get_history_state()
        acquired = board.move(color)
        if acquired != 0 or f_dummy:
            move, score = evaluate(board, depth + 1)
            if score[player_num] > score_best[player_num]:
                score_best = score
                move_best[player_num] = color
            if depth == 0 and False:
                print(f'{color} -> {score}    ', end='')

        board.undo_to(state)


    if depth == 0 and False:
        print(' ')
    return move_best, score_best


def make_move(board, player):
    move_best, score_best = evaluate(board, depth=0)
    #print(f'best move:{move_best} score:{score_best}\n')

    move = move_best[board.current_player_num]
    if move is None:
        # move_best = (board.current_player.color + 1) % len(board.palette_colors)
        move = board.current_player.color
    return move
