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
# ...But...eh... this is broken, as the counterexample with [(1, 5), (10, 3), (10, 3), (16, 5)]
# shows: after considering [(10, 3), (10, 3)], it disregards (1, 5) completely, and
# converges on [(16, 5), (10, 3)] as the best choice, which is not correct; the best choice
# should be [(16, 5), (1, 5)].
#
# ---
#
# For a given warrior H_a, D_a, if we were to choose it as the second, the battle outcome
# is determined by the first warrior (h, d) like so: f(h, d) = h * (d + D_a) + H_a * D_a
#
# Then for two warriors we can tell when pairing with one is better than with the other:
# h * (d + D_a) + H_a * D_a > h * (d + D_b) + H_b * D_b
# h * (D_a - D_b) > H_b * D_b - H_a * D_a
#
# Without loss of generality, suppose D_a > D_b. Then if H_b * D_b <= H_a * D_a, pairing up
# with warrior a is always better; otherwise there is a point when it is better to pair up
# with warrior b - for warriors with health less than (H_b * D_b - H_a * D_a)/(D_a - D_b)
#
# We can then rank all warriors, and end up with a list of seconds whose D_a is strictly
# increasing, and H_a * D_a is strictly decreasing.
#
# According to this, (10, 3) is a better second than (1, 5) only for warriors with health
# less than 12.5, which is apparent if you look at the printout of each-with-each, and
# consider only those pairs where the second is either (10, 3) or (1, 5).
#
# ---
#
# So we need to organize the warriors in a sorted list ordered by the "deciding" health level
# of the first warrior:
#
# ..., (h_i, w_i), (h_i+1, w_i+1), ...
#
# such that for any warrior w_i it is a better second than w_i+1 for health of the first warrior
# less than h_i+1. Consequently, w_i is better than w_i-1 for health of the first warrior
# greater than h_i.
#
# We can add new warriors to such a list in O(log N) time, using binary search for insertion
# point, starting from the middle of the list:
# - if w_i is better than W for health less than H > h_i, we insert in the right sublist.
# - if W is better than w_i for health less than H < h_i, we insert in the left sublist.
# - if w_i is better than W for any health, we discard W.
# - if W is better than w_i for any health, we discard the left sublist, and insert in the right sublist.
#
# So we build such a structure for all N warriors in O(N * logN) time, then in O(N) find the
# best first warrior and his runner-up. If the best first warrior is the same as the second,
# we may be are pairing up this warrior with himself. If runner-up is also the same as the best,
# then we are not pairing up this warrior with himself - we are pairing up the best and the
# runner-up. Otherwise we remove the best warrior from the list, and rebuild the structure,
# and see if the best warrior we found before still pairs up with the same warrior; if so,
# we know there are more than one warrior like that, and we are not pairing the warrior with
# himself; otherwise, we choose the best battle cost from this pairing-up and the runner-up
# from the first round.

from typing import List

def getMaxDamageDealt(N: int, H: List[int], D: List[int], B: int) -> float:
  if not H:
     return 0

  if len(H) == 1:
     return H[0] * D[0] / B

  HD = list(zip(H, D))

  maxd, f, s = maxDmg(HD, rank(HD))
  return maxd / B

# rank produces a list of warriors that are any good to be the second. The produced list is:
# [(health, (damage, health_damage, unique))]
# - health is the health of the first at or below which the preceding warriors are better as the second
# - damage is the D_i of this warrior
# - health_damage is the H_i * D_i of this warrior
# - unique is the flag whether this warrior is unique (should be skipped, when pairing up with himself)
#          if unique, it is the index of the warrior in the original HD; -1, if not unique
def rank(HD):
   HD = [(d, h * d, i) for i, (h, d) in enumerate(HD)]
   HD.sort() # now D_i >= D_j for i >= j

   maxs = []
   for da, hda, i in HD:
      ua = True
      while maxs and maxs[-1][1] <= hda:
         # assert: d_b <= d_a, so if hd_b <= hd_a then  warrior b is not better than a for any health
         if maxs[-1][0] == da and maxs[-1][1] == hda:
            ua = False
         maxs.pop()
      maxs.append((da, hda, i if ua else -1))

   # now work out health levels when the preceding warrior is better than the next warrior
   # the health may be a floating point number with unknown accuracy, but we'll assume
   # that they are not off by 1
   return [(0, maxs[0])] + [((hdb - hda) / (da - db), (da, hda, ua)) for (da, hda, ua), (db, hdb, _) in zip(maxs[1:], maxs)]

def maxDmg(HD, rank):
   # assert: HD is at least 2 long
   # assert: rank is at least 1 long
   j = rank[0][1][-1]
   if len(rank) == 1 and j >= 0:
      # ok, we have one best second; so no point trying any other second with the others
      # also, since we can't match this to himself, need to try all others with this one as the first
      i = HD[j]
      HD = HD[:j] + HD[j+1:]
      return max([hh for j in HD for hh in [m(i, j), m(j, i)]], key=lambda x: x[0])

   rank = [(h, d, hd, i >= 0) for (h, (d, hd, i)) in rank]

   maxd = 0
   for ch, cd in HD:
      chd = ch * cd
      lo, hi = 0, len(rank)
      while lo < hi:
         i = (lo + hi) // 2
         if rank[i][0] < ch:
            lo = i + 1
         else:
            hi = i

      lo -= 1
      if (cd, chd, True) == rank[lo][1:]:
         # ok, current warrior is the same as the best fitting; find someone else to pair up with

         # assert: rank is at least 2 long, because we check that if there is only one best second
         #         and he is unique, then we do not enter this binary search

         # try later one, as all the preceding are going to be worse for ch as per binary search
         lo += 1
         if lo >= len(rank):
            # ok, current warrior was the last in the list - try the preceding guy then
            lo -= 2
            # assert: lo is never less than 0 - we weave around the case of single best second warrior
      _, pd, phd, pu = rank[lo]
      d = ch * (cd + pd) + phd
      if d > maxd:
         maxd = d
         fh, fd, s = ch, cd, rank[lo]

   return maxd, (fd, fh * fd, fh), s

def m(i, j):
   hi, di = i
   hj, dj = j
   return hi * (di + dj) + hj * dj, i, j

def getMaxDamageDealt1(N, H, D, B):
   HD = list(zip(H, D))
   maxs = [m(i, j) for x, i in enumerate(HD) for j in (HD[:x]+HD[x+1:])]
   maxs.sort()
   return maxs

#print(getMaxDamageDealt1(0, [1, 2, 3, 4, 5, 6, 7, 8], [3, 4, 1, 2, 7, 8, 5, 6], 1))
print(getMaxDamageDealt(0, [1, 2, 3, 4, 5, 6, 7, 8], [3, 4, 1, 2, 7, 8, 5, 6], 1))
print(getMaxDamageDealt(3, [2, 1, 4], [3, 1, 2], 4)) # 6.5
print(getMaxDamageDealt(4, [1, 1, 2, 100], [1, 2, 1, 3], 8)) # 62.75
print(getMaxDamageDealt(4, [1, 1, 2, 3], [1, 2, 1, 100], 8)) # 62.75


print(getMaxDamageDealt1(0, [1, 10, 10, 16], [5, 3, 3, 5], 1))
print(getMaxDamageDealt(0, [1, 10, 10, 16], [5, 3, 3, 5], 1)) # 165