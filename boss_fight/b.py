# N warriors with health H_i and damage D_i are fighting the boss which deals damage B.
# Choose two warriors to go into battle so that they deal the greatest damage, and tell
# how long they will last.
#
# Eg first two warriors deal combined damage to the boss, until the frontline warrior
# is defeated, then the second warrior keeps dealing damage until the second one is
# defeated.
#
# --------
#
# ok, the problem is about maximizing H_i * (D_i + D_j) + H_j * D_j - and the result is
# that number divided by B, as the first warrior will be defeated in H_i / B amount of
# time, and the second warrior in H_j / B amount of time.
#
# So for each pair of (i, j) we can choose the order. But going through all pairs is too
# slow - it will be O(N^2), so we need to eliminate checking some pairs.
#
# Suppose we know (i, j) is the best pair for a sublist of warriors. Then considering
# another warrior, k, we can tell that if (i, k) or (j, k) is the new best pair among
# i, j and k, then we don't need to compare k to the rest of warriors in the sublist
# where i and j were the best pair.
#
# ---
# Hmmm... one of the tests doesn't pass

from typing import List

def getMaxDamageDealt(N: int, H: List[int], D: List[int], B: int) -> float:
  return maxDmg(list(zip(H, D))) / B

def maxDmg(HD):
   if not HD:
      return 0

   if len(HD) == 1:
      return HD[0][0] * HD[0][1]

   def m(i, j):
      hi, di = i
      hj, dj = j
      return hi * (di + dj) + hj * dj

   def mm(i, j):
      hi, hj = m(i, j), m(j, i)
      return (hj, i, j) if hi < hj else (hi, j, i)

   maxd, i, j = mm(HD[0], HD[1])
   for k in HD[2:]:
      maxd, i, j = max([(maxd, i, j), mm(k, i), mm(k, j)])
   return maxd

print(getMaxDamageDealt(3, [2, 1, 4], [3, 1, 2], 4)) # 6.5
print(getMaxDamageDealt(4, [1, 1, 2, 100], [1, 2, 1, 3], 8)) # 62.75
print(getMaxDamageDealt(4, [1, 1, 2, 3], [1, 2, 1, 100], 8)) # 62.75
print(getMaxDamageDealt(3, [2000000000, 1000000000, 4000000000], [3000000000, 1000000000, 2000000000], 4000000000)) # 6.5e9
print(getMaxDamageDealt(4, [1000000000, 1000000000, 2000000000, 3000000000], [1000000000, 2000000000, 1000000000, 100000000000], 8000000000)) # 62.75e9
