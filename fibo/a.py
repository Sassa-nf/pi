def fract(n):
   def f(b, e, s):
      return b if b + s > e else (f(b, e, s << 1), f(b + s, e, s << 1))
   return f(0, n, 1)
#
#print(fact(10))
#print()
#print(fact(20))

def fact(n, xs=None):
   if n == 0:
      return 1

   shifts = [0]

   def f(b, e, s, sh, shifts, xs):
      if b == 2:
         b = b >> 1
         e = e >> 1
         s = s >> 1
         sh += 1
      if b + s > e:
         #print(b, e, sh)
         shifts[0] += sh
         return b

      x = f(b, e, s << 1, sh, shifts, xs)
      y = f(b + s, e, s << 1, sh, shifts, xs)
      r = x * y
      if xs is not None:
         xs.append((x.bit_length(), y.bit_length(), r.bit_length()))
      return r

   return f(1, n, 1, 0, shifts, xs) << shifts[0]


def highestBit(n):
   n = (n & 0x55555555) + ((n >> 1) & 0x55555555)
   n = (n & 0x33333333) + ((n >> 2) & 0x33333333)
   n = (n & 0x0f0f0f0f) + ((n >> 4) & 0x0f0f0f0f)
   return (n & 0x00ff00ff) + ((n >> 8) & 0x00ff00ff)

def fact2(n):
   if n == 0:
      return 1

   b = highestBit(n)
   f = 1
   x = 1
   shifts = 0
   nums = 0
   numsofar = [[]]
   while b >= 0:
      n1 = n >> b

      f = f * f
      numsofar.append([y for y in numsofar[-1]])
      while x <= n1:
         numsofar[-1].append(x)
         f = f * x
         x += 2
         nums += 1
      shifts += nums * b
      b -= 1

   print(numsofar)
   return f << shifts


# we don't need to multiply even numbers at all
def fact3(n):
   if n == 0:
      return 1

   nums = []
   while n:
      n1 = n >> 1

      nums.append([x for x in range(n1 + 2 if n1 & 1 else n1 + 1, n + 1, 2)])

      n = n1

   #print(nums)
   nums.reverse()
   p = 1
   shifts = 0
   ds = 0
   b = len(nums)
   prev = 1
   for ns in nums:
      b -= 1
      ds += len(ns)
      shifts += ds * b
      pp = 1
      for x in ns:
         pp *= x
      print('%s * %s = %s' % (prev, pp, prev * pp))
      prev = prev * pp
      p *= prev
   print('----------')
   return p << shifts

for i in range(11):
   print(fact3(i))
#print(fact(63))
#fact3(256*1024)


print('-------------------')
print('burn the candle on both ends:')
ys = []
xs = [x for x in range(1, 2001)]
l = len(xs) - 1
while l > 0:
   i = 0
   while i < l - i:
      x = xs[i]
      y = xs[l - i]
      r = x * y
      xs[i] = r
      ys.append((x.bit_length(), y.bit_length(), r.bit_length()))
      i += 1
   if i == l - i:
      l = i
   else:
      l = i - 1

   xs = xs[0:l+1]
   xs.sort(key=lambda x: x.bit_length())
res_candle = xs[0]

print('-------------------')
print('even-odd:')
xs = []
res_interlace = fact(2000, xs)
xs.sort(key=lambda x: (x[2], x[0], x[1]))
ys.sort(key=lambda x: (x[2], x[0], x[1]))
dx = (0, 0, 0)
for x, y in zip(xs, ys):
   print('%d * %d = %d' % (x[0] - y[0], x[1] - y[1], x[2] - y[2]))
   dx = dx[0] + x[0] - y[0], dx[1] + x[1] - y[1], dx[2] + x[2] - y[2]
print(res_candle == res_interlace, dx)
