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
# repeatedly, memoize. Since N is very large, can't do recursion.

from typing import List

def getMaxExpectedProfit(N: int, V: List[int], C: int, S: float) -> float:
   memo = {}
   solution = 0
   spine = [V[0]] if V else []

   while spine:
      k = (spine[-1], len(spine) - 1)
      if len(spine) == len(V):
         v1, v2 = 0, 0
      else:
         k1 = (V[len(spine)], len(spine))
         v1 = memo.get(k1)
         if v1 is None:
            spine.append(k1[0])
            continue

         k2 = (k1[0] + (1-S) * spine[-1], k1[1])
         v2 = memo.get(k2)
         if v2 is None:
            spine.append(k2[0])
            continue
      solution = max(v1 + spine[-1] - C, v2)
      memo[k] = solution
      spine.pop()

   return solution

print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 5, 0.0), 25)
print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 5, 1.0), 9)
print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 3, 0.5), 17)
print(getMaxExpectedProfit(0, [10, 2, 8, 6, 4], 3, 0.15), 20.10825)
