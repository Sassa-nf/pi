# Given N pages with M links, find the biggest number of different
# pages you can visit. You are allowed to visit same page many times,
# but each unique page is only counted once.
#
# ---
#
# Depth-first traversal of the graph, keeping track of which nodes have
# been visited before in two ways:
#
# - potential loops - a stack of nodes that may still be back-referenced from some children
# - known sizes of subtrees
#
# Loops are known to be complete, when we traversed all children
# of all children of a potential loop. This is the time when we adjust sizes
# of subtrees of all nodes in the loop, so that when anyone reaches any of the
# nodes of the loop in some future traversals, they get the size of the largest
# subtree reachable from some node of the loop.

from typing import List

def getMaxVisitableWebpages(N: int, M: int, A: List[int], B: List[int]) -> int:
  graph = {}
  for f, t in zip(A, B):
     graph.setdefault(f, set()).add(t)
     graph.setdefault(t, set())
  return loops(graph)

def first(s):
   for p in s:
      return p
   return None

def loops(g):
   stack = []     # list of nodes currently reachable from some loops
   seen = {}      # map of nodes to their position in stack
   traversal = [] # sets of outbound edges still to traverse
   loop = []      # indices of loop start on stack
   sizes = {} # node to longest suffix length
   while g:
      p = first(g)
      loop.append(len(stack))
      seen[p] = len(stack)
      traversal.append((p, len(stack), g.pop(p)))
      stack.append(p)
      sizes[p] = 0
      while traversal:
         i, l, s = traversal[-1]
         if s:
            p = first(s)
            s.remove(p)
            if p not in seen:
               if p in sizes: # traversed before in some other branch, and now we know everything about it
                  traversal.append((p, loop[-1]+1, set()))
                  continue
               loop.append(len(stack))
               seen[p] = len(stack)
               traversal.append((p, len(stack), g.pop(p)))
               stack.append(p)
               sizes[p] = 0
               continue
            i = seen[p]
            while loop[-1] > i:
               loop.pop()
            continue
         traversal.pop()
         if l > loop[-1]:
            # assert: traversal is non-empty
            p, _, _ = traversal[-1]
            sizes[p] = max(sizes[p], sizes[i])
            continue
         # now we are popping a loop
         b = loop.pop()
         sz = len(stack) - b + max([sizes[i] for i in stack[b:]])
         for i in stack[b:]:
            sizes[i] = sz
            seen.pop(i)

         stack[b:] = []
         if traversal:
            p, _, _ = traversal[-1]
            sizes[p] = max(sizes[p], sz)
   return max(sizes.values())

print(getMaxVisitableWebpages(4, 4, [1, 2, 3, 4], [4, 1, 2, 1]), 4)
print(getMaxVisitableWebpages(5, 6, [3, 5, 3, 1, 3, 2], [2, 1, 2, 4, 5, 4]), 4)
print(getMaxVisitableWebpages(10, 9, [3, 2, 5, 9, 10, 3, 3, 9, 4], [9, 5, 7, 8, 6, 4, 5, 3, 9]), 5)

xs, ys = zip(*[(1,2), (2, 1), (2, 3), (3, 1), (3, 4), (4, 1), (3, 5), (5, 4), (6, 7), (7, 8), (8, 9), (9, 6), (9, 1), (10, 8), (5, 11)])
print(getMaxVisitableWebpages(10, 9, list(xs), list(ys)), 11)
