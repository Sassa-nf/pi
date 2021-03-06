from neighbours import *

from time import time

MAX_DEPTH = 0
MAX_THREADS = MAX_DEPTH + 1
MAX_ROOTS = 3 * MAX_THREADS
MAX_TIME = 1
MIN_WIDTH = 10000
MAX_WIDTH = 100

def cost(state):
   return sum([len(b) for b in state.boundary])

def find_paths(resume, resume_dict, best_so_far, lives, deadline):
   got_one = 0
   timing = 0
   def explore(s, curr, max_depth):
      # the pruning of unreachable states is done upon entry, but also ensure that we do not produce
      # unreachable state - best_so_far represents the best path that has been found in other threads
      # perhaps; the state of this thread may store a shorter starting point that passes the pruning;
      # need to ensure we do not produce continuations that pruning could not see
      if curr < len(best_so_far):
         c = best_so_far[curr]
         n, s1 = s.transition(c)
         bs = [([c], n, s1)] if n else []
      else:
         bs = [([c], n, s1) for c in range(len(s.boundary)) for n, s1 in [s.transition(c)] if n]
      if not bs:
         return [([], 0, s)]
      if not max_depth:
         return bs

      bs = [(cs + cs1, n + n1, s1) for cs, n, s in bs for cs1, n1, s1 in explore(s, curr+1, max_depth-1)]
      return bs

   while resume:
      if not resume[-1]:
         resume.pop()
         continue
      if got_one and time() > deadline:
         yield None, None, timing
         return

      bs = []
      while resume[-1] and len(bs) < MIN_WIDTH and (not got_one or time() <= deadline):
         path, s = resume[-1].pop()
         if got_one and len(path) >= got_one:
            continue
         t0 = time()
         new_states = [((-len(p), n, cost(s1)), path + p, s1) for p, n, s1 in explore(s, len(path), MAX_DEPTH)]
         for _, p, s1 in new_states:
            same_states = resume_dict.setdefault(s1, [])
            if same_states and same_states[0].path > s1.path:
               # this is possible only if we are exploring worse paths, which can happen only
               # after the better paths have been explored to the end; need to re-link
               # the old results to the new chain
               same_states.insert(0, (p, s1))
            else:
               same_states.append((p, s1))
         bs.extend(new_states)
         timing += time() - t0
      if not bs:
         continue
      bs.sort(key=lambda b: b[0])
      if bs[-1][0][-1] == 0:
         path = bs[-1][1]
         if not got_one or got_one > len(path):
            got_one = len(path)
            yield list(path), bs[-1][-1], timing
            timing = 0
         continue
      bs = [(p, s) for _, p, s in bs]
      resume.append(bs)
   yield None, None, timing

class Game:
   def __init__(self):
      self.best_path = []
      self.steps = 0
      self.suspended = []

   def move(self, board, lives):
      self.steps += 1
      if self.steps <= MAX_THREADS:
         if self.steps == 1:
            colours = max([max(b) for b in board]) + 1
            ns = [set() for _ in range(colours)]
            board_model = Board(board)
            start_colour = board_model.stains[0].colour
            ns[start_colour] = {0}
            _, start = State(0, board_model, 0, ns).transition(start_colour)
            self.best_path = [start_colour]
         else:
            start = self.best_history[self.steps]
         best_so_far = self.best_path[:self.steps]
         suspended = [[(best_so_far, start)]]
         self.suspended = [suspended] + self.suspended
      else:
         best_so_far = self.best_path[:self.steps]

      deadline = time() + MAX_TIME
      while time() < deadline and self.suspended:
         suspended = self.suspended.pop(0)
         while self.suspended and not suspended:
            suspended = self.suspended.pop(0)

         if not self.suspended and not suspended:
            break
         self.suspended.append(suspended)

         # discard unexplorable states
         for i in range(len(suspended)):
            suspended[i] = [(p, s) for p, s in suspended[i]
                                   if (best_so_far[:len(p)] == p if len(p) <= len(best_so_far)
                                       else (len(p) < len(self.best_path) and p[:self.steps] == best_so_far))]
         if self.steps <= MAX_ROOTS and suspended:
            # pick the second best from the existing root
            # - assuming the best is somewhere further along the list of suspensions
            while suspended and not suspended[0]:
               suspended.pop(0)
            if suspended:
               suspended = [[suspended[0].pop()]]
               self.suspended.append(suspended)

         self._deep_explore(suspended, best_so_far, lives, deadline)

      min_p = self.best_path

      if self.steps >= len(min_p):
         return -1

      if self.steps == len(min_p) - 1:
         print('Done! in %s steps' % self.steps)
      return min_p[self.steps]

   def _deep_explore(self, suspended, best_so_far, lives, deadline):
      min_p = self.best_path
      # find_paths finds at least one path, and the path has at least one node, because we start
      # with empty state that can only transition to board.stains[0]
      its = []
      s = None
      for p, s1, it in find_paths(suspended, best_so_far, lives, deadline):
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


   def make_move(self, mainboard, player):
      board = [[c if c >= 0 else mainboard.player[-c].color for c in b] for b in mainboard.field]
      return self.move(board, player.life)

def new_game():
   return Game()
