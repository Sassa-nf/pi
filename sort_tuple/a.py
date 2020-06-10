# https://leetcode.com/explore/challenge/card/june-leetcoding-challenge/539/week-1-june-1st-june-7th/3352/#
# Suppose you have a random list of people standing in a queue. Each person is described by a pair of
# integers (h, k), where h is the height of the person and k is the number of people in front of this
# person who have a height greater than or equal to h. Write an algorithm to reconstruct the queue.
#
# Note:
# The number of people is less than 1,100.
#
#
# Example
#
# Input:
# [[7,0], [4,4], [7,1], [5,0], [6,1], [5,2]]
#
# Output:
# [[5,0], [7,0], [5,2], [6,1], [4,4], [7,1]]

from functools import reduce

def reconstructQueue(people): # List[List[int]]) -> List[List[int]]:
   queue = []
   ppl = [(p[1], p) for p in people]
   ppl.sort(key=lambda p: -p[0])

   while ppl:
      p = ppl.pop()
      p, ppl = reduce(lambda a, q: (q, a[1] + [a[0]]) if q[0] == 0 and q[1][0] <= a[0][1][0] else (a[0], a[1] + [q]), ppl, (p, []))

      queue.append(p[1])
      ppl = [p if p[1][0] > queue[-1][0] else (p[0] - 1, p[1]) for p in ppl]
      for q in range(len(ppl)):
         if ppl[q][0] == 0:
            p = q
            break
   return queue
#def reconstructQueue(people):
#   queue = [None for _ in people]
#   positions = [i for i in range(len(people))]
#   people.sort(key=lambda p: (-p[0], p[1]))
#
#   while people:
#      p = people.pop()
#      i = positions.pop(p[1])
#      queue[i] = p
#   return queue

print('%s' % reconstructQueue([[7,0], [4,4], [7,1], [5,0], [6,1], [5,2]]))
