# a rotating lock with two dials.
# each dial has 1..N digits. Rotating the dial by 1 in any direction takes 1 second.
# To select a digit, you can rotate either of the dials.
# 
# Given N, M (number of digits) and [Int] (a list of numbers), find the smallest time
# needed to select all these digits in turn.
#
# eg
# N = 10
# M = 4
# [9, 4, 4, 8]
# ------------
# rotate disk 1 by -2 to get to 9; select 9 | +2 seconds
# rotate disk 2 by 3 to get to 4; select 4  | +3 seconds
# stay still; select 4                      | +0 seconds
# rotate disk 1 by -1 to get to 8; select 8 | +1 seconds
# ------------------------------------------------------
#                                              6 seconds


# N <= 1G
# M <= 3000
# ok, here's my thinking:
# descending down the shortest path is going to miss cases (will only find local minima);
# 2^3000 options is too many; however, there are going to be many cases where we don't need
# to trackback/retry:
#
# let's assume two dials are at positions A and B, and we need to explore whether they can
# be moved to C and D; the thing is, if A needs to go past B to get to both C and D, then
# moving A cannot be more optimal:
# * Suppose C is closer than D: without loss of generality, A < C < D
#   - if it is also the case that A < B < C, then (C-B) + (D-A) = (D-B) + (C-A) - so we can move B to
#     D, and decide whether to move A to C
#   - if A < C < B, then we need to test whether moving A or B to C is more optimal


# Actually, let's look at it differently. All of the above was based on the problem that
# the possible paths are too numerous. This is not so, however, as we can rule out all
# the paths that lead to the same configuration.
#
# For each digit D_i there are only (i-1) possible previous configurations. (That is, one
# of the disks is stopped at one of the (i-1) previous digits, so the second disk does all
# the moves from that digit D_j at position j up to D_i at position i.) This makes for only
# M^2 configurations to keep track of, so we will be fine with memoisation and breadth-first
# search of the shortest path to each configuration.

def dt(t1, t2, N):
   return min(t2 + N - t1, t1 - t2) if t2 < t1 else min(t2 - t1, t1 + N - t2)

def update(cfg, p1, p2, t0):
   if p1 > p2:
      p1, p2 = p2, p1

   t1 = cfg.get((p1, p2))
   if t1 is None or t0 < t1:
      cfg[(p1, p2)] = t0

def shortestTime(N, M, xs):
   if not xs:
      return 0

   t0 = dt(1, xs[0], N)
   cfg = {(1, xs[0]): t0}
   for d in xs[1:]:
      nex = {}
      for (p1, p2), c in cfg.items():
         update(nex, d, p2, c + dt(p1, d, N))
         update(nex, d, p1, c + dt(p2, d, N))
      cfg = nex

   return min(cfg.values())


print(shortestTime(10, 4, [9, 4, 4, 8]))

xs = [k for i in range(1, 3000 // 2 +1) for k in [500000000 - i + 1, i + 1]]
print(shortestTime(1000000000, len(xs), xs))
