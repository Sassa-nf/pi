def remove_isles(mx):
   ps = []
   for i, c in enumerate(mx[0]):
      if not c:
         continue
      ps.append((i, 0))

   for i, c in enumerate(mx[-1]):
      if not c:
         continue
      ps.append((i, len(mx)-1))

   for j, r in enumerate(mx[1:-1]):
      if r[0]:
         ps.append((0, j+1))
      if r[-1]:
         ps.append((len(r)-1, j+1))

   reachable = set(ps)
   ns = []
   while ps:
      x, y = ps.pop()
      if not ps:
         ps = ns
         ns = []
      for c, r in [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]:
         if c < 0 or r < 0 or c >= len(mx[0]) or r >= len(mx) or (c, r) in reachable or not mx[r][c]:
            continue
         reachable.add((c, r))
         ns.append((c, r))

   return [[v if (c, r) in reachable else 0 for c, v in enumerate(m)] for r, m in enumerate(mx)]

def remove_isles2(mx):
   reachable = [[0]*len(r) for r in mx]
   reachable[0] = mx[0]
   reachable[-1] = mx[-1]

   ps = []
   for i, c in enumerate(mx[0]):
      if not c:
         continue
      ps.append((i, 0))

   for i, c in enumerate(mx[-1]):
      if not c:
         continue
      ps.append((i, len(mx)-1))

   for j, r in enumerate(mx[1:-1]):
      if r[0]:
         ps.append((0, j+1))
         reachable[j+1][0] = r[0]
      if r[-1]:
         ps.append((len(r)-1, j+1))
         reachable[j+1][-1] = r[-1]

   ns = []
   while ps:
      x, y = ps.pop()
      if not ps:
         ps = ns
         ns = []
      for c, r in [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]:
         if c < 0 or r < 0 or c >= len(mx[0]) or r >= len(mx) or reachable[r][c] or not mx[r][c]:
            continue
         reachable[r][c] = mx[r][c]
         ns.append((c, r))

   return reachable

mx1 = [
   [1, 0, 0, 0, 0, 0],
   [0, 1, 0, 1, 1, 1],
   [0, 0, 1, 0, 1, 0],
   [1, 1, 0, 0, 1, 0],
   [1, 0, 1, 1, 0, 0],
   [1, 0, 0, 0, 0, 1],
   ]
print(remove_isles2(mx1))
