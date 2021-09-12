# given [a, b, c, d, ...], compute last decimal digit of a^(b^(c^(d^...)))
#
# corner cases:
# last_digit([]) == 1
# last_digit([0, 0]) == 1

def last_digit(lst):
   if not lst:
      return 1

   if len(lst) == 1:
      return lst[0] % 10

   if lst[-1] == 0:
      return last_digit(lst[:-2])

   if 0 in lst:
      lst.reverse()
      idx = lst.index(0)
      lst = lst[idx:]
      lst.reverse()
      return last_digit(lst)

   if 1 in lst:
      idx = lst.index(1)
      return last_digit(lst[:idx])

   # assert: now we have to compute a^x, where x is definitely not 0 and not 1
   r = lst[0] % 10
   if r in {0, 1, 5, 6}:
      return r

   # assert: r in {2, 3, 4, 7, 8, 9}
   #
   # (2 ** i) % 10 in {2, 4, 8, 6}
   # (3 ** i) % 10 in {3, 9, 7, 1}
   # (4 ** i) % 10 in {4, 6}
   # (7 ** i) % 10 in {7, 9, 3, 1}
   # (8 ** i) % 10 in {8, 4, 2, 6}
   # (9 ** i) % 10 in {9, 1}
   #
   # as we can see, all cycles are either 2 or 4, so we don't need to know the full (r ** i),
   # we only need to find the remainder of the last cycle
   #
   # so we need to find b^(c^(d^...)) % 4
   #
   # now, same analysis for b % 4:
   b = lst[1] % 4

   # (0 ** i) % 4 in {0}
   # (1 ** i) % 4 in {1}
   # (2 ** i) % 4 in {0} for i > 1, in {2} for i == 1
   # (3 ** i) % 4 in {3, 1}

   if len(lst) > 2:
      if b == 2: # i > 1; since 1s have been eliminated, 2^1 is just 2, or len(lst) == 2
         b = 0
      elif b == 3 and lst[2] % 2 == 0: # even powers produce even remainders, so (3 ** (2*i)) % 4 == 1
         b = 1
   if b == 0: # b is (b ** i) % 4; we don't want a^0, so pick the next power that produces the same remainder
      b = 4
   return (r ** b) % 10 # r and b are small enough for r ** b to fit into int

print(last_digit([12, 30, 21]))
print(last_digit([937640, 767456, 981242]))
print(last_digit([123232, 694022, 140249]))
print(last_digit([499942, 898102, 846073]))
print(last_digit([2147483647, 2147483647, 2147483647, 2147483647]))
