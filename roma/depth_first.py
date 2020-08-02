from neighbours import *

from time import time

MAX_DEPTH = 5
MAX_TIME = 1
MAX_WIDTH = 100

def cost(state):
   return sum([len(b) for b in state.boundary])

def find_paths(resume, lives, dt):
   deadline = time() + dt

   got_one = 0
   iters = 0
   def explore(s, max_depth):
      bs = [([c], n, s1) for c in range(len(s.boundary)) for n, s1 in [s.transition(c)] if n]
      if not bs:
         bs = [([], 0, s)]
      if not max_depth:
         return bs

      bs = [(cs + cs1, n + n1, s1) for cs, n, s in bs for cs1, n1, s1 in explore(s, max_depth-1)]
      return bs

   while resume:
      if not resume[-1]:
         resume.pop()
         continue
      if got_one and time() > deadline:
         yield None, None, iters
         return

      bs = []
      while resume[-1] and (not bs or got_one and len(bs) < MAX_WIDTH):
         path, s = resume[-1].pop()
         if got_one and len(path) >= got_one:
            continue
         iters += 1
         bs += [((-len(p), n, cost(s1)), path + p, s1) for p, n, s1 in explore(s, MAX_DEPTH)]
      if not bs:
         continue
      bs.sort(key=lambda b: b[0])
      if bs[-1][0][-1] == 0:
         path = bs[-1][1]
         if not got_one or got_one > len(path):
            got_one = len(path)
            yield list(path), bs[-1][-1], iters
         continue
      # discard duplicate states; ignore the difference in colour, because we are only interested in whether
      # the coverage and the neighbours are the same - that is, whether we can switch to the same colours
      # from there
      bs = ([(bs[i][1], bs[i][2]) for i in range(len(bs)-1)
                                  if bs[i+1][0] != bs[i][0] or bs[i+1][2] != bs[i][2]] +
            [(bs[-1][1], bs[-1][2])])
      resume.append(bs)
   yield None, None, iters

class Game:
   def __init__(self):
      self.best_path = []
      self.steps = 0
      self.suspended = []

   def move(self, board, lives):
      if self.steps <= MAX_DEPTH:
         self.steps += 1
         if not self.suspended:
            colours = max([max(b) for b in board]) + 1
            ns = [set() for _ in range(colours)]
            board_model = Board(board)
            start_colour = board_model.stains[0].colour
            ns[start_colour] = {0}
            _, start = State(0, board_model, set(), ns).transition(start_colour)
            self.best_path = [start_colour]
         else:
            start = self.best_history[self.steps]
         suspended = [[(self.best_path[:self.steps], start)]]
         self.suspended.append(suspended)
      else:
         self.steps += 1

         best_so_far = self.best_path[:self.steps]
         suspended = self.suspended.pop(0)
         while self.suspended and not suspended:
            suspended = self.suspended.pop(0)
         self.suspended.append(suspended)

         # discard unexplorable states
         for i in range(len(suspended)):
            suspended[i] = [(p, s) for p, s in suspended[i]
                                   if (best_so_far[:len(p)] == p if len(p) <= len(best_so_far)
                                       else (len(p) < len(self.best_path) and p[:self.steps] == best_so_far))]

      min_p = self.best_path

      # find_paths finds at least one path, and the path has at least one node, because we start
      # with empty state that can only transition to board.stains[0]
      its = []
      s = None
      for p, s1, it in find_paths(suspended, lives, MAX_TIME):
         its.append(it)
         if p is None:
            break
         s = s1
         min_p = p
      print('Found a path: %d %s; iterations: %s' % (len(min_p), min_p, its))
      old_history = None
      if self.steps == 1 or len(self.best_path) > len(min_p):
         if self.steps > 1:
            old_history = self.best_history
         self.best_path = min_p
         self.best_history = []
         p = s
         while p:
            self.best_history.append(p)
            p = p.parent
         self.best_history.reverse()
      else:
         min_p = self.best_path
         print('Best path so far still: %d %s > %s' % (len(min_p), min_p[:self.steps], min_p[self.steps:] if self.steps < len(min_p) else []))

      if self.steps >= len(min_p):
         return -1

      if self.steps == len(min_p) - 1:
         print('Done! in %s steps' % self.steps)
      return min_p[self.steps]

   def make_move(self, mainboard, player):
      board = [[c if c >= 0 else mainboard.player[-c].color for c in b] for b in mainboard.field]
      return self.move(board, player.life)

def new_game():
   return Game()
