#def fact(n):
#   def f(b, e, s):
#      return b if b + s > e else (f(b, e, s << 1), f(b + s, e, s << 1))
#   return f(0, n, 1)
#
#print(fact(10))
#print()
#print(fact(20))

def fact(n):
   if n == 0:
      return 1

   shifts = [0]

   def f(b, e, s, sh, shifts):
      if b == 2:
         b = b >> 1
         e = e >> 1
         s = s >> 1
         sh += 1
      if b + s > e:
         #print(b, e, sh)
         shifts[0] += sh
         return b

      x = f(b, e, s << 1, sh, shifts)
      y = f(b + s, e, s << 1, sh, shifts)
      return x * y

   return f(1, n, 1, 0, shifts) << shifts[0]


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
