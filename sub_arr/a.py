# https://leetcode.com/contest/biweekly-contest-28/problems/find-two-non-overlapping-sub-arrays-each-with-target-sum/
# Given an array of integers arr and an integer target.
#
# You have to find two non-overlapping sub-arrays of arr each with sum equal target.
# There can be multiple answers so you have to find an answer where the sum of the
# lengths of the two sub-arrays is minimum.
#
# Return the minimum sum of the lengths of the two required sub-arrays, or return -1
# if you cannot find such two sub-arrays.
#
from functools import reduce

def minSum(arr, target):
   def step(a, x):
      b, e, s = a[-1]
      if x < 0:
         a[-1] = (e+1, e+1, 0)
      else:
         s += x
         while s > target:
            s -= arr[b]
            b += 1
         a[-1] = (b, e+1, s)
         if s == target:
            a.append((b+1, e+1, s - arr[b]))
      return a
   r = reduce(step, arr, [(0, 0, 0)])
   r.pop()

   found = None

   while len(r) >= 2:
      j = min(range(len(r)), key=lambda j: (r[j][1] - r[j][0], -r[j][0]))
      w = r[j]
      l1 = w[1] - w[0]

      k = j - 1
      while k >= 0 and r[k][1] > w[0]:
         k -= 1
      l = j + 1
      while l < len(r) and r[l][0] < w[1]:
         l += 1
      print("R: %s, J: %s, K: %s, L: %s" % (r, j, k, l))

      vs = [min(rs, key=lambda v: (v[1] - v[0], -v[0])) for rs in [r[:k+1], r[l:]] if rs]
      if vs:
         v = min(vs, key=lambda v: v[1] - v[0])
         l0 = v[1] - v[0]
         if found is None or found > l0 + l1:
            found = l0 + l1

      if len(vs) < 2:
         # it makes sense to continue only if both head and tail are non-empty:
         # in that case there can be an interval in the head and an interval in the tail that
         # overlap with w, but don't overlap between themselves
         #
         # if either the head or the tail is empty, then the unexplored part consists of intervals
         # that all overlap between themselves, so no need to explore
         break
      r = r[k+1:j] + r[j+1:l]

   return -1 if found is None else found

#print(minSum([3,2,2,4,3], 3))
#print(minSum([7,3,4,7], 7))
#print(minSum([4,3,2,6,2,3,4], 6))
#print(minSum([5,5,4,4,5], 3))
#print(minSum([3,1,1,1,5,1,2,1], 3))
#
#i = [78,18,1,94,1,1,1,29,58,3,4,1,2,56,17,19,4,1,63,2,16,11,1,1,2,1,25,62,10,69,12,7,1,6,2,92,4,1,61,7,26,1,1,1,67,26,2,2,70,25,2,68,13,4,11,1,34,14,7,37,4,1,12,51,25,2,4,3,56,21,7,8,5,93,1,1,2,55,14,25,1,1,1,89,6,1,1,24,22,50,1,28,9,51,9,88,1,7,1,30,32,18,12,3,2,18,10,4,11,43,6,5,93,2,2,68,18,11,47,33,17,27,56,13,1,2,29,1,17,1,10,15,18,3,1,86,7,4,16,45,3,29,2,1,1,31,19,18,16,12,1,56,4,35,1,1,36,59,1,1,16,58,18,4,1,43,31,15,6,1,1,6,49,27,12,1,2,80,14,2,1,21,32,18,15,11,59,10,1,14,3,3,7,15,4,55,4,1,12,4,1,1,53,37,2,5,72,3,6,10,3,3,83,8,1,5]
#t = 97
#
#print(minSum(i, t))

#i = [1000] * 1000000 + [1, 999] + [1000] * 499999
#t = 500000000
i = [4] * 6 + [1, 1] + [2] * 9
t = 20
print(minSum(i, t)) # should be 15, but isn't

