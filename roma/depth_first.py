from neighbours import *

from time import time

MAX_DEPTH = 5
MAX_TIME = 1

def cost(state):
   return sum([len(b) for b in state.boundary])

def find_paths(resume, lives, dt):
   deadline = time() + dt

   got_one = 0
   def explore(s, max_depth):
      bs = [([c], n, s1) for c in range(len(s.boundary)) for n, s1 in [s.transition(c)] if n]
      if not bs:
         bs = [([], 0, s)]
      if not max_depth:
         return bs

      bs = [(cs + cs1, n + n1, s1) for cs, n, s in bs for cs1, n1, s1 in explore(s, max_depth-1)]
      return bs

   def paths(resume):
      nonlocal got_one
      while resume:
         if not resume[-1]:
            resume.pop()
            continue
         if got_one and time() > deadline:
            return

         path, s = resume[-1].pop()
         if got_one and len(path) >= got_one:
            continue
         bs = [((-len(p), n, cost(s1)), p, s1) for p, n, s1 in explore(s, MAX_DEPTH)]
         bs.sort(key=lambda b: b[0])
         # discard duplicate states; ignore the difference in colour, because we are only interested in whether
         # the coverage and the neighbours are the same - that is, whether we can switch to the same colours
         # from there
         bs = ([(bs[i][1], bs[i][2]) for i in range(len(bs)-1)
                                     if bs[i+1][0] != bs[i][0] or bs[i+1][2] != bs[i][2]] +
               [(bs[-1][1], bs[-1][2])])
         if len(bs[-1][0]) <= MAX_DEPTH:
            path = path + bs[-1][0]
            if not got_one or got_one > len(path):
               got_one = len(path)
               yield list(path)
            continue
         resume.append([(path + cs, s) for cs, s in bs])
   return paths(resume)

class Game:
   def __init__(self):
      self.best_path = []
      self.steps = 0

   def move(self, board, lives):
      self.steps += 1

      colours = max([max(b) for b in board]) + 1
      ns = [set() for _ in range(colours)]
      board = Board(board)
      ns[board.stains[0].colour] = {0}
      start = State(0, board, set(), ns)
      min_p = [board.stains[0].colour]
      # find_paths finds at least one path, and the path has at least one node, because we start
      # with empty state that can only transition to board.stains[0]
      for p in find_paths([[([], start)]], lives, MAX_TIME):
         min_p = p
      print('Found a path: %d %s' % (len(min_p), min_p))
      if not self.best_path or len(self.best_path) > len(min_p):
         self.best_path = min_p
      else:
         min_p = self.best_path
         print('Best path so far still: %d %s' % (len(min_p), min_p))
      self.best_path = self.best_path[1:]
      if len(self.best_path) == 1:
         print('Done!')
      if len(min_p) < 2:
         return -1
      return min_p[1]

   def make_move(self, mainboard, player):
      board = [[c if c >= 0 else mainboard.player[-c].color for c in b] for b in mainboard.field]
      return self.move(board, player.life)

def new_game():
   return Game()
