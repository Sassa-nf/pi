# construct a regex to match all binary representations of numbers divisible by 3
#
# let's start with a function that matches binary strings

def div3(s):
   while s:
      if s[-1] == '0': # is a multiple of ...0
         s = s[:-1]
         continue
      # assert: s[-1] == '1'
      if len(s) < 2:
         return False
      c = s[-2]
      s = s[:-2]
      if c == '1': # assert: was s.endswith('11') - is a multiple of ...01
         continue
      # assert: was s.endswith('01')
      if len(s) < 2:
         return False
      # is a multiple of ...11; let's subtract 11 * 11 - that is 1001, and 01 was chopped off already
      if s[-2] == '1':
         s = s[:-2] + '0' + s[-1]
         continue
      # borrow 1
      c = '1' + s[-1]
      s = s[:-2]
      while s.endswith('0'):
         s = s[:-1]
         c = '1' + c
      # assert: s.endswith('1')
      s = s[:-1] + '0' + c
   return True


r = [i for i in range(1000000) if div3(bin(i)[2:]) != (i % 3 == 0)]
if not r:
   print('ok')
else:
   print(bin(r[0]))
