from neighbours import *

INF = float('+inf')

def a_star(start, finished, neighbours, heuristic):
   suggestions = {start}
   path = dict()
   g_score = dict()
   g_score[start] = 0
   f_score = dict()
   f_score[start] = heuristic(start)
   while suggestions:
      current = min(suggestions, key=lambda x: f_score.get(x, INF))
      if finished(current):
         return path
      suggestions.remove(current)
      for n, cost in neighbours(current):
         t = g_score.get(current, INF) + cost
         if t < g_score.get(n, INF):
            path[n] = current
            g_score[n] = t
            f_score[n] = t + heuristic(n)
            suggestions.add(n)

def move(board, lives):
   colours = max([max(b) for b in board]) + 1
   ns = [set() for _ in range(colours)]
   board = Board(board)
   ns[board.stains[0].colour] = {0}
   start = State(0, board, set(), ns)
   def finished(s):
      return not s.boundary
   def neighbours(s):
      return [(s, 1.0 / n)for n, s in [s.transition(c) for c in range(len(s.boundary))] if n]
   def heuristic(s):
      return 0

   p = a_star(start, finished, neighbours, heuristic)
   return board, p
