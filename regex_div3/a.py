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
   if s[-2] == '1': # assert: s.endswith('11') - is a multiple of ...01
      return div3(s[:-2])

   return div3_01(s[:-2])

def div3_01(s):
   # assert: was s.endswith('01')
   while s.endswith('11'):
      s = s[:-2]

   if len(s) < 2:
      return False
   # is a multiple of ...11; let's subtract 11 * 11 - that is 1001, and 01 was chopped off already
   if s[-2] == '1':
      # assert: s[-1] == '0'
      return div3(s[:-2])

   # assert: s[-2] == '0'
   if s[-1] == '1':
      # borrow 1
      return borrow1(s[:-2])
   return borrow1_00(s[:-2])

def borrow1(s):
   while s.endswith('00'):
      s = s[:-2]

   if s.endswith('0'):
      # assert: s.endswith('10') - and we borrow it, so it turns into 01
      return div3_01(s[:-2])
   # assert: s.endswith('1') - and we borrow it, so it turns into 0
   return div3(s[:-1])

def borrow1_00(s):
   while s.endswith('00'):
      s = s[:-2]

   if s.endswith('0'):
      # assert: s.endswith('10') - and we borrow it, so it turns into 01, plus carry
      return div3(s[:-2])
   # assert: s.endswith('1') - and we borrow it, so it turns into 0, plus carry
   return div3_01(s[:-1])

#r = [i for i in range(1000000) if div3(bin(i)[2:]) != (i % 3 == 0)]


# ok, so BNF for the above is
# div3_01 = div3_01 11 | div3 10 | borrow1 01 | borrow1_00 00
# borrow1 = borrow1 00 | div3_01 10 | div3 1
# borrow1_00 = borrow1_00 00 | div3 10 | div3_01 1

# which is, after inlining:
#
# div3 = '' | div3 0 | div3 11 | div3_01 01
# div3_01 = div3 10 (00)* 1* | div3_01 100 (00)* 1*
def div31(s):
   if not s:
      return True
   if s[-1] == '0':
      return div31(s[:-1])
   if s.endswith('11'):
      return div31(s[:-2])
   if s.endswith('01'):
      return div31_01(s[:-2])
   return False

def div31_01(s):
   while s.endswith('1'):
      s = s[:-1]
   while s.endswith('00'):
      s = s[:-2]
      if s.endswith('1'):
         return div31_01(s[:-1])
   if s.endswith('10'):
      return div31(s[:-2])
   return False

#r = [i for i in range(1000000) if div31(bin(i)[2:]) != (i % 3 == 0)]

# after more inlining:
#
# div3 = '' | div3 0 | div3 11 | div3 10 (00)* 1* (100 (00)* 1*)* 01
#
# the regex then is: (0 | 11 | 10 (00)* 1* (100 (00)* 1*)* 01)+
# which can be further simplified to:
# (0 | 11 | 10 (00)* (1+ (00)+)* 1* 01)+
#
# which is:
# (0 | 1 (00)* 1 | 10 (00)* 1 ((00)* 1)* 01)+

import re

#DIV_3 = re.compile(r'(0|11|10(00)*(1+(00)+)*1*01)+')
#DIV_3 = re.compile(r'^(0|1(00)*1|10((00)*1)+01)+$')
DIV_3 = re.compile(r'^(0|11|10(00)*(1+(00)+)*1*01)+$')

#r = [i for i in range(10000000) if (not DIV_3.match(bin(i)[2:])) != (i % 3 != 0)]

def rem3(s):
   if not s:
      return 0

   if s[0] == '0':
      return rem3(s[1:])

   return rem3_1(s[1:])

def rem3_1(s):
   if not s:
      return 1

   if s[0] == '1':
      return rem3(s[1:])

   return rem3_10(s[1:])

def rem3_10(s):
   if not s:
      return 2

   if s[0] == '0':
      return rem3_1(s[1:])

   return rem3_10(s[1:])

#r = [i for i in range(10000000) if rem3(bin(i)[2:]) != i % 3]


# ok, BNF for the above is:
# rem3 = '' | 0 rem3 | 1 rem3_1
# rem3_1 = 1 rem3 | 0 rem3_10
# rem3_10 = 0 rem3_1 | 1 rem3_10
#
# which after inlining is:
# rem3 = '' | 0 rem3 | 1 rem3_1
# rem3_1 = 1 rem3 | 0 rem3_10
# rem3_10 = 1* 0 rem3_1
#
# rem3 = '' | 0 rem3 | 1 rem3_1
# rem3_1 = 1 rem3 | 0 1* 0 rem3_1
#
# rem3 = '' | 0 rem3 | 1 rem3_1
# rem3_1 = (0 1* 0)* 1 rem3
#
# rem3 = '' | 0 rem3 | 1 (0 1* 0)* 1 rem3
#
# so the regex is:

REM3 = re.compile(r'^(0|1(01*0)*1)+$')

#r = [i for i in range(10000000) if (not REM3.match(bin(i)[2:])) != (i % 3 != 0)]

# rem_0 = 0 | 1 rem_1
# rem_1 = 0 rem_2 | 1 rem_3
# rem_2 = 1 rem_0 | 0 rem_4
# rem_3 = 0 rem_1 | 1 rem_2 => rem_1 = 0 rem_2 | 1 0 rem_1 | 1 1 rem_2 = (1 0)* (0 | 1 1) rem_2
# rem_4 = 0 rem_3 | 1 rem_4 => rem_4 = 1* 0 rem_3 => rem_2 = 1 rem_0 | 0 1* 0 rem_3 = 1 rem_0 | 0 1* 0 0 rem_1 | 0 1* 0 1 rem_2 = (0 1* 0 1)* (1 rem_0 | 0 1* 0 0 rem_1)
#
# rem_1 = (1 0)* (0 | 1 1) (0 1* 0 1)* (1 rem_0 | 0 1* 0 0 rem_1) = ((1 0)* (0 | 1 1) (0 1* 0 1)* 0 1* 0 0)* (1 0)* (0 | 1 1) (0 1* 0 1)* 1 rem_0
#
# rem_0 = (0 | 1 ((1 0)* (0 | 1 1) (0 1* 0 1)* 0 1* 0 0)* (1 0)* (0 | 1 1) (0 1* 0 1)* 1)+

REM5 = re.compile(r'^(0|1((10)*(0|11)(01*01)*01*00)*(10)*(0|11)(01*01)*1)+$')
r = [i for i in range(10000000) if (not REM5.match(bin(i)[2:])) != (i % 5 != 0)]

if not r:
   print('ok')
else:
   print(bin(r[0]))
