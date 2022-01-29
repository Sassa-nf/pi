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
# So we group horizontal lines by y - O(N*log(N)), the cost of sorting, - and keep
# track of x positions at which vertical lines are crossing y. Updating this view
# of vertical lines is O(N*log(N)) - finding insertion or deletion position; special
# care is taken to ensure we do not keep copying bits of list for each insertion.
# Given a view of vertical lines, finding the number of crosses is also O(N*log(N)) -
# binary search for each horizontal line.
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

def match(horz, vert):
   ys = [v for x, vs in vert for y0, y1 in vs if y1 - y0 > 1 for v in [(y0 + 1, x), (y1, x)]]
   ys.sort(key=lambda x: -x[0])

   vs = [] # positions where vertical lines are for a row at y
   cross = 0
   for y, hs in horz:
      xs = []
      while ys and ys[-1][0] <= y:
         xs.append(ys.pop()[1])
      if xs:
         xs.sort()

         prev = xs[0]
         c = 0
         xs1 = []
         for x in xs:
            if x == prev:
               c += 1
               continue
            if c & 1:
               xs1.append(prev)
            prev = x
            c = 1

         if c & 1:
            xs1.append(prev)

         vs1 = []
         j = 0
         for x in xs1:
            i = bin_search(vs, x)
            vs1.extend(vs[j:i])
            if i < len(vs) and vs[i] == x:
               j = i+1
            else:
               vs1.append(x)
               j = i
         vs1.extend(vs[j:])
         vs = vs1

      for x0, x1 in hs:
         if x1 - x0 == 1:
            continue
         i0, i1 = bin_search(vs, x0 + 1), bin_search(vs, x1)
         cross += i1 - i0

   return cross

print(getPlusSignCount(0, [6, 3, 4, 5, 1, 6, 3, 3, 4], 'ULDRULURD'), 4)
print(getPlusSignCount(0, [1, 1, 1, 1, 1, 1, 1, 1], 'RDLUULDR'), 1)
print(getPlusSignCount(0, [1, 2, 2, 1, 1, 2, 2, 1], 'UDUDLRLR'), 1)

horz = [500002, 1] * 500000
d = 'RULU' * 250000
vert = [1, 500002] * 500000
d = d + ('RDRU' * 250000)
print(getPlusSignCount(0, horz + vert, d), 500000 ** 2)
