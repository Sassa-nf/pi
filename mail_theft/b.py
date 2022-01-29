# Given the value of arriving mail packages, the probability of theft,
# and the fee paid to collect un-stolen mail packages, maximize profit.
#
# So, a store room accumulates packages of value V_i, and charges C to
# enter and collect all the remaining packages. If you don't collect,
# they may get stolen with probability S.
#
# Number of packages, 1 <= N <= 4000
# Value of packages, 0 <= V_i <= 1000
# Cost of collecting, 1 <= C <= 1000
# Probability of theft, 0.0 <= S <= 1.0
#
# ---
#
# Try N ways to choose the first day to collect mail. For each of those,
# solve the smaller problem. Since we will be evaluating same stuff
# repeatedly, memoize.

from typing import List

def getMaxExpectedProfit(N: int, V: List[int], C: int, S: float) -> float:
   memo = {}
   return solve(V, C, S, memo)

def solve(v, c, s, memo):
   if not v:
      return 0
   k = (v[0], len(v))
   m = memo.get(k)
   if m is not None:
      return m

   m = max(0, v[0] - c)
   if len(v) > 1:
      if m > 0:
         m += solve(v[1:], c, s, memo)
      v[1] += v[0] * (1 - s)
      m = max(m, solve(v[1:], c, s, memo))
   memo[k] = m
   return m

print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 5, 0.0), 25)
print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 5, 1.0), 9)
print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 3, 0.5), 17)
print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 3, 0.15), 20.10825)
