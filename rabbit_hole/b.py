# Given N pages with M links, find the biggest number of different
# pages you can visit. You are allowed to visit same page many times,
# but each unique page is only counted once.
#
# ---
#
# This is very much like a graph span.
#
# Depth-first walk the graph, looking out for cycles. Replace cycles
# with a node with the outbound to all children of all nodes in the
# cycle, keeping track of the cycle length.
#
# Eg each page is (self, [child]), where self is 1 for normal pages,
# and cycle length for synthetic pages replacing the cycles.

from typing import List

def getMaxVisitableWebpages(N: int, M: int, A: List[int], B: List[int]) -> int:
  graph = {}
  rev = {}
  for f, t in zip(A, B):
     graph.setdefault(f, set()).add(t)
     rev.setdefault(t, set()).add(f)

  return span(graph, rev, list(set(B) - graph.keys()))

def span(g, rev, leaves):
   sizes = {p: 0 for p in g.keys()} # storing the longest branch reachable from each node
   while g:
      while leaves:
         l = leaves.pop()
         sz = sizes.setdefault(l, 0) + 1
         for p in rev.pop(l):
            sizes[p] = max(sizes.setdefault(p, 0) + 1, sz) # choose the longest of branches
            g[p].remove(l)
            if not g[p]:
               g.pop(p)
               if rev.get(p):
                  leaves.append(p)

      if not g:
         break

      # after eliminating leaves all children lead to loops
      for p in g.keys():
         break
      ns = {}
      nn = []
      while g[p]:
         while p not in ns:
            ns[p] = len(nn)
            nn.append(p)
            for p in g[p]:
               break
         sz = len(nn) - ns[p] - 1 # loop length excluding self
         sizes[p] = sizes[p] + sz
         # replace all nodes of the loop with one node - and fixup reverse references.
         # any additional branches parallel to the loop should remain reachable from
         # the loop and their length added in the next iteration

         for n in nn[ns[p]+1:]:
            ps, cs = rem(g, rev, n)
            ps.remove(p)
            cs = cs - {p}
            rev[p] = rev[p].union(ps)
            g[p] = g[p].union(cs)
            sizes[p] = max(sizes[p], sizes[n] + sz)
            ns.pop(n)
            for c in cs:
               rev[c].add(p)
            for c in ps:
               g[c].add(p)
         nn = nn[:ns[p]]
         ns.pop(p)

      # now that g[p] is empty, p is a leaf - or a lone page
      if rev.get(p):
         leaves.append(p)
      else:
         g.pop(p)

   return max(sizes.values()) + 1

def rem(g, rev, n):
   ps, cs = rev.pop(n), g.pop(n)
   for p in ps:
      g[p].remove(n)
   for c in cs:
      rev[c].remove(n)
   return ps, cs

print(getMaxVisitableWebpages(4, 4, [1, 2, 3, 4], [4, 1, 2, 1]), 4)
print(getMaxVisitableWebpages(5, 6, [3, 5, 3, 1, 3, 2], [2, 1, 2, 4, 5, 4]), 4)
print(getMaxVisitableWebpages(10, 9, [3, 2, 5, 9, 10, 3, 3, 9, 4], [9, 5, 7, 8, 6, 4, 5, 3, 9]), 5)

xs, ys = zip(*[(1,2), (2, 1), (2, 3), (3, 1), (3, 4), (4, 1), (3, 5), (5, 4), (6, 7), (7, 8), (8, 9), (9, 6), (9, 1), (10, 8), (5, 11)])
print(getMaxVisitableWebpages(10, 9, list(xs), list(ys)), 11)
