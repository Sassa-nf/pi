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
  memo = {}
  return fixMin(R, 0, 0, A, B, memo)

def fixMin(R, i, b, A, B, memo):
   # assuming R[i] is fixed, must adjust left and right sublists of discs;
   # doing so incurs a baseline cost;
   # then once we adjusted disc sizes, check what is the min cost of the
   # sublists
   baseline = 0
   max_r = R[i] - i
   xs = R[:i]
   for j, r in enumerate(xs):
      dx = r - (j + max_r)
      if dx > 0:
         baseline += dx * B
         xs[j] -= dx
   min_r = R[i] + 1
   ys = R[i+1:]
   for j, r in enumerate(ys):
      dx = j + min_r - r
      if dx > 0:
         baseline += dx * A
         ys[j] += dx

   return baseline + findMin(xs, b+i, R[i], b, A, B, memo) + findMin(ys, b+i, R[i], b+i+1, A, B, memo)

def findMin(R, i, ri, b, A, B, memo):
   if not R:
      return 0

   r = memo.get((i, ri, R[0]))
   if r is not None:
      return r

   r = min([fixMin(R, j, b, A, B, memo) for j in range(len(R))])
   memo[(i, ri, R[0])] = r
   return r

print(getMinimumSecondsRequired(0, [100, 100, 100], 7, 3), 9) # 9
print(getMinimumSecondsRequired(0, [100, 100, 100], 2, 3), 5) # 5
print(getMinimumSecondsRequired(0, [6, 5, 4, 3], 10, 1), 19) # 19
print(getMinimumSecondsRequired(0, [100, 100, 1, 1], 2, 1), 207) # 207
print(getMinimumSecondsRequired(0, [6, 5, 2, 4, 4, 7], 1, 1), 10) # 10
