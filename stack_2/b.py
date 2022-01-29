from typing import List

# Given a stack of discs of sizes, work out the time needed to resize all discs so that
# the disc sizes are in increasing order.
#
# N - number of discs;                      1 <= N <= 50
# R - the list of disc sizes                1 <= R <= 1e9
# A - time needed to increase any disc by 1 1 <= A <= 100
# B - time needed to decrease any disc by 1 1 <= B <= 100
#     (obviously, can't decrease disc size, if that will make its size 0)
#
# --------
# 

def getMinimumSecondsRequired(N: int, R: List[int], A: int, B: int) -> int:
  R = [0] + R
  memo = [[] for _ in R]

  # adjust R to make sure the discs are not smaller than their position in list
  # - that is the smallest they are allowed to be; this incurs the baseline cost
  baseline = 0
  for i, r in enumerate(R):
     if r < i:
        baseline += A * (i - r)
        R[i] = i
  cost = findMin(R, 1, A, memo) # we didn't resize disc 0
  # now let's work out the cost, if we don't resize some other disc (which means
  # potentially making preceding discs smaller)

  return baseline + cost

def bin_search(xs, x, key = None):
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

def findMin(R, i, A, memo):
   if i >= len(R):
      return 0

   r_i = R[i]

   if R[i] < R[i-1]:
      R[i] = R[i-1] + 1

   m = memo[i]
   j = bin_search(m, R[i], lambda x: x[0])
   if j < len(m) and m[j][0] == R[i]:
      cost = m[j][1]
   else:
      cost = A * (R[i] - r_i) + findMin(R, i+1, A, memo)
      m.insert(j, (R[i], cost))
   R[i] = r_i
   return cost
