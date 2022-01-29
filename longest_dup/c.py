def longest_dup(S):
   C = [ord(c) for c in S]
   def find_l(l):
      if not l:
         return None

      s = sum(C[:l])
      sums = {s: [0]}
      i = l
      j = 0
      while i < len(S):
         s += C[i] - C[j]
         poss = sums.setdefault(s, [])
         i += 1
         j += 1
         poss.append(j)

      for vs in sums.values():
         vals = set()
         for v in vs:
            s = S[v:v+l]
            if s in vals:
               return s
            vals.add(s)
      return None
   begin, end = 0, len(S)
   f = ''
   while begin < end:
      i = (begin + end) // 2
      ff = find_l(i)
      if ff:
         f = ff
         begin = i + 1
      else:
         end = i
   return f
print(longest_dup('banana'))
