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
   def queue(ppl):
      if not ppl:
         return
      pivot = min(ppl, key=lambda a: (a[1], a[0]))
      bigger = queue([p for p in ppl if p[0] > pivot[0]])
      smaller = queue([p for p in ppl if p[0] <= pivot[0] and p != pivot])

      yield pivot

      n = pivot[1]
      for s in smaller:
         for _, b in zip(range(n+1, s[1]), bigger):
            yield b
         yield s
         n = s[1] # actually, this is not a sufficient condition
      for b in bigger:
         yield b
   return list(queue(list(people)))
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
