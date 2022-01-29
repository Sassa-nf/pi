from random import randint, shuffle
from functools import reduce

def doh1(xs):
   r = 0
   n = len(xs)
   should = n >> 1
   m = 0
   while should:
      actual = 0
      for x in xs:
         actual += (x >> m) & 1
      if should < actual:
         r += 1 << m
      m += 1
      should = n >> m
      should = ((should >> 1) << m) + (n & ((1 << m) - 1) if should & 1 else 0)
   return r
def doh11(xs):
   ys = [-sum([j & (1 << i) for j in range(len(xs))]) for i in range(32)]
   for x in xs:
      for i in range(32):
         ys[i] += x & (1 << i)
   ys.reverse()
   return reduce(lambda r, y: (r << 1) + (y > 0), ys, 0)

def doh2(xs):
   begin, end = 0, len(xs)
   while begin + 1 < end:
      i = (begin + end) // 2
      s = sum([begin < x <= i for x in xs])
      if s > i - begin:
         end = i
      else:
         begin = i
   return end

def doh(xs):
   begin, end = 0, len(xs)
   while begin + 1 < end:
      i = begin + (end - begin) // 3
      i2 = (i + end + 1) // 2
      s1 = 0
      s2 = 0
      for x in xs:
        if x <= i:
            s1 += begin < x
        else:
            s2 += x <= i2
      if s1 > i - begin:
         end = i
      elif s2 > i2 - i:
         begin = i
         end = i2
      else:
         begin = i2
   return end

def tortoise(xs):
   t, h = xs[0], xs[xs[0]]
   while t != h:
      t = xs[t]
      h = xs[xs[h]]
   t = 0
   while t != h:
      t = xs[t]
      h = xs[h]
   return h

print(doh1([13, 2, 3, 13, 13, 6, 7, 13, 9, 10, 11, 12, 13, 13]))
print(doh1([1, 1]))
print(tortoise([13, 2, 3, 13, 13, 6, 7, 13, 9, 10, 11, 12, 13, 13]))
print(tortoise([1, 1]))
for _ in range(100000):
   sz = randint(1, 200)
   extra = randint(1, sz)
   repeats = randint(1, sz + 1)
   inp = list(range(1, sz + 1))
   shuffle(inp)
   inp = inp[:sz + 1 - repeats] + [extra]*repeats
   shuffle(inp)

   d = doh1(inp)
   if d != extra:
      print('DOH! %s != %s for %s' % (d, extra, inp))

import time
ITERS = 100
xs = list(range(1, 65535)) + [2]
t0 = time.time()
for _ in range(ITERS):
   doh1(xs)
t1 = time.time()
for _ in range(ITERS):
   tortoise(xs)
t2 = time.time()

print('DOH: %.6f\nTortoise: %.6f' % ((t1-t0) / ITERS, (t2-t1) / ITERS))
