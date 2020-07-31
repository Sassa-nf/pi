from neighbours import *

from time import time

def find_paths(start, lives, dt):
   deadline = time() + dt
   path = []

   got_one = 0
   def paths(s):
      nonlocal got_one
      if got_one and (
          time() > deadline or
          len(path) >= got_one or
          len(path) >= lives):
         return
      bs = [(-n, c, s1) for c in range(len(s.boundary)) for n, s1 in [s.transition(c)] if n]
      bs.sort()
      if not bs:
         got_one = len(path)
         yield list(path)
      for _, c, s1 in bs:
         path.append(c)
         for p in paths(s1):
            yield p
         path.pop()
   return paths(start)

def move(board, lives):
   colours = max([max(b) for b in board]) + 1
   ns = [set() for _ in range(colours)]
   board = Board(board)
   ns[board.stains[0].colour] = {0}
   start = State(0, board, set(), ns)
   min_p = [board.stains[0].colour]
   # find_paths finds at least one path, and the path has at least one node, because we start
   # with empty state that can only transition to board.stains[0]
   for p in find_paths(start, lives, 2):
      min_p = p
   print('Found a path: %d %s' % (len(min_p), min_p))
   return min_p[1 if len(min_p) > 1 else 0]

def make_move(mainboard, player):
   board = [[c if c >= 0 else mainboard.player[-c].color for c in b] for b in mainboard.field]
   return move(board, player.life)
