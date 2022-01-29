# Tunnels along a circular track at positions (A_i, B_i), inclusive, they do not
# overlap. Find the amount of wall clock time that elapses by the time the train
# spends time K in tunnels.

from typing import List

def getSecondsElapsed(C: int, N: int, A: List[int], B: List[int], K: int) -> int:
   return elapsed(C, list(zip(A, B)), K)

def elapsed(c, tuns, k):
   tuns.sort()
   s = 0
   for a, b in tuns:
      s += b - a
   full_rots = (k - 1) // s
   k -= full_rots * s

   # we could do even binary search, but we already have O(N) cost, no need to
   # complicate
   for a, b in tuns:
      s = b - a
      if k <= s:
         break
      k -= s
   return full_rots * c + k + a

print(getSecondsElapsed(10, 2, [1, 6], [3, 7], 7), 22)
print(getSecondsElapsed(50, 3, [39, 19, 28], [49, 27, 35], 15), 35)
