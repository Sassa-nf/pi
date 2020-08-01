from inkspill import *
import depth_first_v0 as ai
import depth_first as d_ai

from time import time

def run():
   mainboard = Board(boardWidth, boardHeight, paletteColors)
   d_mainboard = Board(boardWidth, boardHeight, paletteColors, mainboard)
   ai.new_game()
   d_game = d_ai.new_game()

   orig_board = [[c if c >= 0 else mainboard.player[-c].color for c in b] for b in mainboard.field]
   steps = [0, 0]
   times = [0, 0]
   for i, (m, board) in enumerate([(ai, mainboard), (d_game, d_mainboard)]):
      c = 0
      while not steps[i]:
         c += 1
         t0 = time()
         color = m.make_move(board, board.player[1])
         times[i] += time() - t0
         board.move(1, color)
         if board.has_won(1):
            steps[i] = c
         elif board.player[1].life == 0:
            steps[i] = -c
   return zip(steps, times), orig_board

results = []
for _ in range(100):
   (ai_r, d_ai_r), board = run()
   print('Last known good Depth-first: %s steps, %.3f seconds' % ai_r)
   print('Depth-first: %s steps, %.3f seconds' % d_ai_r)
   print('PASS' if d_ai_r[0] <= ai_r[0] else ('FAIL\n\n' + '\n'.join([''.join([str(c) for c in b]) for b in board])))
   print('-----------------------------------')
   results.append((ai_r, d_ai_r))
   if d_ai_r[0] > ai_r[0]:
      break
print(results)
