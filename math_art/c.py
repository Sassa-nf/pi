# Given a list of drawing instructions, count how many crosses are drawn.
#
# Drawing instructions consist of pen movement direction (LURD) and integer
# offset of that movement.
#
# Number of lines: 2 <= N <= 2M
# Offsets: 1 <= L <= 1G
# Directions: D_i in 'LURD'
#
# ---
#
# Let's collect all vertical lines and all horizontal lines, grouping them
# by the same coordinate. The weird thing here is that matching each line with
# each is too expensive, so we need to reduce the amount of searching for matches.
#

from typing import List

def getPlusSignCount(N: int, L: List[int], D: str) -> int:
   horz = {}
   vert = {}
   x, y = 0, 0
   for o, d in zip(L, D):
      if d == 'D':
         vert.setdefault(x, []).append((y - o, y))
         y -= o
      elif d == 'U':
         vert.setdefault(x, []).append((y, y + o))
         y += o
      elif d == 'L':
         horz.setdefault(y, []).append((x - o, x))
         x -= o
      else:
         horz.setdefault(y, []).append((x, x + o))
         x += o
   return match(organize(horz), organize(vert))

def organize(horz):
   res = []
   for k, vs in horz.items():
      vs.sort()
      ls = [vs[0]]
      for a, b in vs[1:]:
         if b <= ls[-1][1]:
            continue
         if a <= ls[-1][1]:
            a = ls.pop()[0]
         ls.append((a, b))
      res.append((k, ls))
   res.sort()
   return res

def bin_search(xs, x, key=None):
   if key is None:
      key = lambda x: x
   lo, hi = 0, len(xs)
   while lo < hi:
      i = (lo + hi) // 2
      if key(xs[i]) < x:
         lo = i + 1
      else:
         hi = i

   return lo

def pick_lines(vert, x0, x1):
   i0 = bin_search(vert, x0 + 1, key=lambda x: x[0])
   i1 = bin_search(vert, x1, key=lambda x: x[0])
   yys = [(x, ys) for x, ys in vert[i0:i1] if ys]
   yys.sort(key=lambda ys: ys[1][0][1])
   for _, ys in yys:
      if ys[0][1] > y:
         break
      while ys and ys[0][1] <= y:
         ys.pop(0)
   yys = [(x, ys) for x, ys in yys if ys]
   # assert: yys is a list of vertical lines that end above y
   yys.sort(key=lambda ys: ys[1][0][0])
   while yys and yys[-1][1][0][0] >= y:
      yys.pop()
   # assert: yys is a list of vertical lines that cross ((x0, y), (x1, y))
   yys.sort(key=lambda ys: -ys[1][0][1]) # the lines that end lower/sooner are at the end
   return i0, i1, yys


def match(horz, vert):
   cross = 0
   for y, hs in horz:
      if not hs:
         continue
      for x0, x1 in hs:
         i0, i1, yys = pick_lines(vert, x0, x1)
         x0, ys = min(yys, key=lambda x: x[0])
         j0, j1, xxs = pick_lines(horz, ys[0][0], ys[0][1])
         while yys:
            x1, vs = yys.pop()
         vert[i0: i1] = [(x, ys) for x, ys in vert[i0: i1] if ys]

   return cross

print(getPlusSignCount(0, [6, 3, 4, 5, 1, 6, 3, 3, 4], 'ULDRULURD'), 4)
print(getPlusSignCount(0, [1, 1, 1, 1, 1, 1, 1, 1], 'RDLUULDR'), 1)
print(getPlusSignCount(0, [1, 2, 2, 1, 1, 2, 2, 1], 'UDUDLRLR'), 1)

horz = [500002, 1] * 500000
d = 'RULU' * 250000
vert = [1, 500002] * 500000
d = d + ('LDLU' * 250000)
print(getPlusSignCount(0, horz + vert, d), 500000 ** 2)
