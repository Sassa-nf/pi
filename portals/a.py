# Given a maze with portals, find the shortest path from S to E.
#
# A maze consists of cells marked {'.', '#', 'a'...'z', 'S', 'E'}.
# There is exactly one 'S', one or more 'E', and any number of other
# cells. '.' means empty cell, '#' is a wall, 'a'...'z' is a portal,
# connecting to other cells with the same letter.
#
# If there is no path from 'S' to any 'E', return -1.
#
# ---
#
# Well, this is breadth-first exploration of the maze.

from typing import List

def getSecondsRequired(R: int, C: int, G: List[List[str]]) -> int:
   portals = {}
   start = []
   for r, row in enumerate(G):
      for c, cell in enumerate(row):
         if 'a' <= cell <= 'z':
            portals.setdefault(cell, []).append((r, c))
         elif cell == 'S':
            start = [(r, c)]
            seen = {(r, c)}
   if not start:
      return -1
   return traverse(G, portals, start, seen)

def traverse(maze, portals, ns, seen):
   nn = []
   path = 1
   while ns:
      r, c = ns.pop()
      cell = maze[r][c]
      neigh = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)] + portals.get(cell, [])
      for n in neigh:
         r, c = n
         cell = maze[r][c] if 0 <= r < len(maze) and 0 <= c < len(maze[r]) else '#'
         if cell == '#' or n in seen:
            continue
         if cell == 'E':
            return path
         seen.add(n)
         nn.append(n)

      if not ns:
         path += 1
         ns = nn
         nn = []
   return -1
