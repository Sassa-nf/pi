# Given a list of integers representing scores of players, what is the minimal number of tasks
# if each task could only provide 1, 2 or 3 points to each player.
from typing import List

def getMinProblemCount(N: int, S: List[int]) -> int:
   # assert: all numbers are better off represented as multiples of 3, with one
   #         extra task potentially representing a task with fewer than 3 points
   #
   # Let's assume that for all scores with the same remainder we are constrained
   # below by the ability to represent the smallest score with that remainder, and
   # any other number with the same remainder can be obtained by adding 3-point tasks.
   #
   # So we keep track of the smallest and the biggest scores for each remainder,
   # and then work out the smallest number of tasks with corresponding points, and
   # given that many tasks, the biggest number of 3-point tasks needed to represent
   # the biggest scores.

   mins = [None] * 3
   maxs = [0] * 3
   for s in S:
      r = s % 3
      if maxs[r] == 0:
         mins[r] = s
         maxs[r] = s
      else:
         mins[r] = min(s, mins[r])
         maxs[r] = max(s, maxs[r])

   rems = [0] * 3
   if mins[1] is not None:
      # assert: maxs[1] is also set - it is 3 * n + 1
      #
      # we choose to claim a 1-point task or two 2-point tasks:
      #
      # - if mins[1] == 1, there is need for n == 0, we have to have a 1-point task
      # - if mins[2] is None, there is no gain from choosing two 2-point tasks to
      #   represent maxs[1] = 3 * n + 1 = 3 * (n-1) + (2 + 2)
      # - if maxs[1] < maxs[0], there is possibly a gain from representing
      #   maxs[0] = 3 * (n+1) as maxs[0] = 3 * n + (1 + 2)
      #
      # otherwise:
      # mins[1] > 1, mins[2] > 1, maxs[1] can be represented as 3 * (n-1) + (2 + 2),
      # so requires fewer 3-point tasks - can help reduce the number of 3-point tasks
      # required
      if mins[1] == 1 or mins[2] is None or maxs[1] < maxs[0]:
         rems[1] = 1 # a 1-point task is required
         rems[0] = maxs[1] // 3
      else:
         rems[2] = 2 # 2 + 2 is the same as 1 + 3, but since we already know 2-point is required...
         rems[0] = (maxs[1] - 4) // 3
   if mins[2] is not None:
      if rems[2] == 0:
         rems[2] = 1
      rems[0] = max(rems[0], maxs[2] // 3)
   if maxs[0] > 0:
      rems[0] = max(rems[0], (maxs[0] - (3 if rems[1] and rems[2] else 0)) // 3)
   return sum(rems)

def getMinProblemCount1(n, S):
   def f(cs, s):
      if not cs:
         return max(s)
      choice1 = f(cs[1:], s)
      choice2 = choice1
      for v in s:
         if v >= cs[0]:
            choice2 = 1 + f(cs, [v - cs[0] if v >= cs[0] else v for v in s])
            break
      return min(choice1, choice2)
   return f([3, 2, 1], S)

print(getMinProblemCount(0, [2, 4]), 2)
print(getMinProblemCount(0, [2, 5, 7]), 3)
print(getMinProblemCount(0, [2, 8]), 3)
