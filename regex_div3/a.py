# construct a regex to match all binary representations of numbers divisible by 3
#
# let's start with a function that matches binary strings

def div3(s):
   if not s:
      return True

   if s[-1] == '0': # is a multiple of ...0
      return div3(s[:-1])
   # assert: s[-1] == '1'
   if len(s) < 2:
      return False
   c = s[-2]
   s = s[:-2]
   if c == '1': # assert: was s.endswith('11') - is a multiple of ...01
      return div3(s)

   return div3_01(s)

def div3_01(s):
   # assert: was s.endswith('01')
   if len(s) < 2:
      return False
   # is a multiple of ...11; let's subtract 11 * 11 - that is 1001, and 01 was chopped off already
   if s[-2] == '1':
      if s[-1] == '0':
         return div3(s[:-2])
      return div3_01(s[:-2])
   # assert: s[-2] == '0'
   # borrow 1
   return borrow1(s)

def borrow1(s):
   c = '1' + s[-1]
   s = s[:-2]
   while s.endswith('0'):
      s = s[:-1]
      c = '1' + c
   # assert: s.endswith('1')
   return div3(s[:-1] + '0' + c)


r = [i for i in range(1000) if div3(bin(i)[2:]) != (i % 3 == 0)]
if not r:
   print('ok')
else:
   print(bin(r[0]))
