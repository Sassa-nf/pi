"""A board is a graph of neighbours, where each node is a stain of same colour
and the edges connect stains that touch each other.

Then at each step the state can be described as a set of stains that are painted
the same colour, and a union of sets of their neighbours.
"""
class Stain:
   def __init__(self, colour, neighbours):
      self.colour = colour
      self.neighbours = set(neighbours)

   def __str__(self):
      return '%d, %s' % (self.colour, self.neighbours)

class Board:
   def __init__(self, board):
      stains = [Stain(board[0][0], set())]
      self.stains = stains

      bb = [[None for _ in b] for b in board]

      def test(ox, oy, stain):
         def visit(x, y):
            if board[x][y] == board[ox][oy]:
               bb[x][y] = stain
               return True
            stains[stain].neighbours.add((x, y))
            return False
         return visit

      new_stains = [0]
      walk(board, [(0, 0)], test(0, 0, 0))

      while new_stains:
         s = new_stains.pop()
         ns = stains[s].neighbours
         for x, y in ns:
            if bb[x][y] is not None:
               continue
            i = len(stains)
            new_stains.append(i)
            stains.append(Stain(board[x][y], set()))
            walk(board, [(x, y)], test(x, y, i))
         stains[s] = Stain(stains[s].colour, {bb[x][y] for x, y in ns})

   def __str__(self):
      return '\n'.join(['%d: %s' % (i, s) for i, s in enumerate(self.stains)])

class State:
   def __init__(self, path, board, coloured, boundary):
      self.path = path
      self.board = board
      self.coloured = coloured
      self.boundary = boundary

   def __eq__(self, other):
      return self.coloured == other.coloured and self.boundary == other.boundary

   def transition(self, colour):
      new = self.boundary[colour]
      if not new:
         return 0, None

      coloured = self.coloured | new

      boundary = [set(v) for v in self.boundary]
      boundary[colour] = set()
      for s in new:
         for n in self.board.stains[s].neighbours:
            if n in coloured:
               continue
            boundary[self.board.stains[n].colour].add(n)

      return len(new), State(self.path + 1, self.board, coloured, boundary)

def walk(board, queue, f):
   visit = [[True for _ in b] for b in board]
   for x, y in queue:
      visit[x][y] = not f(x, y)
   while queue:
      x, y = queue.pop()
      if x > 0 and visit[x-1][y] and f(x-1, y):
         visit[x-1][y] = False
         queue.append((x-1, y))
      if x < len(board)-1 and visit[x+1][y] and f(x+1, y):
         visit[x+1][y] = False
         queue.append((x+1, y))
      if y > 0 and visit[x][y-1] and f(x, y-1):
         visit[x][y-1] = False
         queue.append((x,y-1))
      if y < len(board[0])-1 and visit[x][y+1] and f(x, y+1):
         visit[x][y+1] = False
         queue.append((x,y+1))
