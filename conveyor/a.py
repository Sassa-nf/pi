# a system of horizontal conveyor belts.
#
# parcels get dropped from above. When they fall on a conveyor
# belt, they move along the direction that the belt is moving in.
#
# You can select one conveyor, and specify the direction of its movement.
# All other conveyors will move in random directions.
#
# Now, the task is to find a solution such that the average
# distance travelled by the parcels is minimal.
#

# It looks like we are dealing with a system of equations:
# for each belt, when moving left:
#
# BL_i = falling from the sky + sum of falling from other belts
#
# Then falling from the sky is decided based on how much of the belt is
# open to the sky, and at which point the parcels land there.
#
# For each belt j there is BL_j + BR_j - that is, some parcels
# fall off the left edge of the belt, and travel the distance determined
# based on the position of the left edge of the belt relative to the
# belt i; some parcels fall off the right edge of the belt, etc.
#
# ...but what do you do with 500K conveyors? if one conveyor depends on 500K,
# we can't afford to recompute that for every try.
# so we actually need to tell the upstream nodes the cost of sending parcels
# down one way. Then the gain is selected by comparing the cost of sending
# them left or sending them right

# N <= 500K - the number of conveyors
# 1 <= H_i < 1M - the altitude at which the conveyor is located
# 0 <= A_i < B_i <= 1M - the horizontal positions of the ends of the conveyor
# 0 <= x <= 1M - the initial horizontal position of the package drop

from typing import List

SKY = ''
def getMinExpectedHorizontalTravelDistance(N: int, H: List[int], A: List[int], B: List[int], names) -> float:
   if not names:
      names = H
   conveyors = list(zip(H, A, B, names))
   conveyors.sort(key=lambda x: (-x[0], x[1], x[2], x[3]))
   sky = [(0, 1000000, SKY)]
   conveyors = [c for _, a, b, n in conveyors
                  for c in [split_sky(sky, a, b, n)] if c]

   maxd = calc(conveyors, 0, 0)
   maxg = 0
   maxdir = 0
   # now propagate the cost of going left or right
   conveyors.reverse()
   for c in conveyors:
      direction, gain = c.choose()
      if maxg > gain:
         maxg = gain
         maxdir = direction
         mini = c

   mind = (maxd + maxg) / 1000000
   print('Found %s should go %s to get min avg distance of: %.6f' % (mini.name, 'left' if maxdir < 0 else 'right', mind))

   return mind

def calc(conveyors, i, d):
   dist = 0
   for j, c in enumerate(conveyors):
      dist += c.reset(d if j == i else 0)
   print('---------------------------')
   return dist

class Conveyor:
   def __init__(self, a, b, xs, n):
      self.name = n
      self.sz = b - a
      self.lr = 0
      self.dl = 0
      self.dr = 0
      self.s = [((x + y) / 2 - a, ('SKY', (lambda d: lambda _: d)(y - x)) if c == SKY else c) for x, y, c in xs]

   def reset(self, lr):
      dl, dr, cs, ns = zip(*[(d * c, (self.sz - d) * c, c, n) for d, (n, f) in self.s for c in [f((self.sz + self.dl + self.dr) / 2)]]) # (d + dl) + (sz - d + dr) = sz + dl + dr
      print('Counts: %s' % (list(zip(ns, cs)),))
      dl = sum(dl)
      dr = sum(dr)
      self.cl, self.cr = sum(cs), 0

      print('Conveyor %s: %s\n for %d does (%d, %d) cl=%d' % (self.name, self.s, lr, dl, dr, self.cl))
      if lr < 0:
         return dl

      if lr == 1:
         self.cl, self.cr = 0, self.cl
         return dr

      self.cl = self.cl / 2
      self.cr = self.cl

      if lr == 2:
         return dl, dr
      return (dl + dr) / 2

   def left(self, d):
      self.dl = d
      return self.cl

   def right(self, d):
      self.dr = d
      return self.cr

   def choose(self):
      dl, dr = self.reset(2)
      gain = self.dl * self.cl + dl / 2 - self.dr * self.cr - dr / 2
      return (-1, gain) if gain < 0 else (1, -gain)

def split_sky(sky, a, b, n):
   print('>', n)
   s, e = bin_search(sky, a, b)
   if e <= s:
      return None
   x, y, t = sky[s]
   if y > x and t == SKY:
      sky.insert(s, (x, a, SKY))
      e += 1
      s += 1
      sky[s] = (a, y, SKY)
      print('> %s' % (sky,))
   x, y, t = sky[e-1]
   if y > x and t == SKY:
      sky.insert(e, (b, y, SKY))
      sky[e-1] = (x, b, SKY)
      print('> %s' % (sky,))
   c = Conveyor(a, b, sky[s:e], n)
   sky[s:e] = [(a, a, (n + ' left', c.left)), (b, b, (n + ' right', c.right))]
   print('> %s\n===========' % (sky,))
   return c

def bin_search(sky, a, b):
   # there is standard bisect(), but it doesn't do projections
   s, e = 0, len(sky)
   while e > s:
      c = (e + s) // 2
      x, y, _ = sky[c]
      if x >= b:
         e = c
         continue
      s = c+1

   s, t = 0, e
   while t > s:
      c = (t + s) // 2
      x, y, _ = sky[c]
      if y <= a:
         s = c + 1
         continue
      t = c
   return s, e

getMinExpectedHorizontalTravelDistance(2, [10, 20], [100000, 400000], [600000, 800000], ['A', 'B']) # 155000, choose B to run to the right
getMinExpectedHorizontalTravelDistance(5, [2, 8, 5, 9, 4], [5000, 2000, 7000, 9000, 0], [7000, 8000, 11000, 11000, 4000], ['A', 'B', 'C', 'D', 'E']) # 36.5, choose C and run to the left
