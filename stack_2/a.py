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
  if len(R) < 2:
     return 0

  result = [(n[:-1], c) for n, c in fixMin(R, [0], A, B) if n[0] > 0]
  _, costs = zip(*result)

  return min(costs)

def bin_search(xs, x, key=None):
   if key is None:
      key = lambda a: a
   lo, hi = 0, len(xs)
   while lo < hi:
      i = (lo + hi) // 2
      if key(xs[i]) < x:
         lo = i + 1
      else:
         hi = i
   return lo

def fixMin(R, prevs, A, B):
   nexts = [p + 1 for p in prevs]
   if not R:
      return [([n], 0) for n in nexts]

   j = bin_search(nexts, R[0])
   if j >= len(nexts) or nexts[j] > R[0]:
      nexts.insert(j, R[0])

   dn_costs = fixMin(R[1:], nexts, A, B)

   def diff(n):
      nonlocal A
      nonlocal B
      nonlocal R
      ri = R[0]
      dx = ri - n
      if dx < 0:
         return -A * dx
      return B * dx

   for i, (ns, cost) in enumerate(dn_costs):
      n = ns[0] - 1
      j = bin_search(nexts, n)
      if j >= len(nexts) or nexts[j] > n:
         nexts.insert(j, n)

   curr_dn = len(dn_costs) - 1
   ns, cost = dn_costs[curr_dn]

   for i in range(len(nexts)-1, -1, -1):
      n = nexts[i]
      while curr_dn > 0:
         ns1, cost1 = dn_costs[curr_dn - 1]
         if ns1[0] <= n:
            break
         curr_dn -= 1
         if cost1 < cost:
            ns, cost = ns1, cost1

      nexts[i] = ([n] + ns, cost + diff(n))
      
   return nexts

print(getMinimumSecondsRequired(0, [100, 100, 100], 7, 3), 9) # 9
print(getMinimumSecondsRequired(0, [100, 100, 100], 2, 3), 5) # 5
print(getMinimumSecondsRequired(0, [6, 5, 4, 3], 10, 1), 19) # 19
print(getMinimumSecondsRequired(0, [100, 100, 1, 1], 2, 1), 207) # 207
print(getMinimumSecondsRequired(0, [6, 5, 2, 4, 4, 7], 1, 1), 10) # 10
