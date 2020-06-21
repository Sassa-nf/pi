def ukkonen(S):
   # Ukkonen Suffix Tree
   BOTTOM = 0
   GS = [{}, {}]
   ROOT = 1
   FS = {ROOT: BOTTOM} # suffixes
   def g(s, t):
      if s is BOTTOM:
         return -1, -1, ROOT
      return GS[s][t]
   def f(s):
      return FS[s]

   def update(s, k, i):
      #print('>>> UPDATE %s, %s' % (S[i] if i >= 0 else -1, (s, k, i)))
      oldr = ROOT
      end, r = test(s, k, i - 1, S[i])
      while not end:
         GS[r][S[i]] = i, len(S) - 1, BOTTOM
         if oldr is not ROOT:
            FS[oldr] = r
         oldr = r
         s, k = canonize(f(s), k, i - 1)
         end, r = test(s, k, i - 1, S[i])
      if oldr is not ROOT:
         FS[oldr] = s
      return s, k

   def canonize(s, k, p):
      if p < k:
         return (s, k)
      k1, p1, s1 = g(s, S[k])
      while p1 - k1 <= p - k:
         k += p1 - k1 + 1
         s = s1
         if k <= p:
            k1, p1, s1 = g(s, S[k])
      return (s, k)

   def test(s, k, p, t):
      if k > p:
         #print('<<< TEST: k > p in %s' % ((s, k, p, t),))
         return s is BOTTOM or (s < len(GS) and t in GS[s]), s
      k1, p1, s1 = g(s, S[k])
      if t == S[k1 + p - k + 1]:
         #print('<<< TEST: char %s is the same as at %s as per %s' % (t, k1 + p - k + 1, ((s, k, p), (k1, p1, s1))))
         return True, s
      #print('<<< TEST: char %s is not the same as %s at %s as per %s' % (t, S[k1 + p - k + 1], k1 + p - k + 1, ((s, k, p), (k1, p1, s1))))
      r = len(GS)
      GS.append({S[k1 + p - k + 1]: (k1 + p - k + 1, p1, s1)})
      GS[s][S[k]] = k1, k1 + p - k, r
      #print('>>> NEW STATES: %s at %s and %s at %s' % (GS[s], s, GS[r], r))
      return False, r

   s = ROOT
   k = 0
   for i in range(len(S)):
      s, k = update(s, k, i)
      s, k = canonize(s, k, i)

   return GS

def print_sfx(indent, s, GS, S):
   for k, p, s in s.values():
      print('%s%s%s' % ('   ' * indent, S[k:p+1], ':' if s else ''))
      print_sfx(indent+1, GS[s], GS, S)

def is_in(S, sfx):
   GS = ukkonen(S)
   print_sfx(0, GS[1], GS, S)
   k, p, s = 0, -1, 1
   while p - k < len(sfx):
      if not sfx.startswith(S[k:p+1]):
         return False
      sfx = sfx[p - k + 1:]
      if not sfx:
         return True
      l = GS[s].get(sfx[0])
      if not l:
         return False
      k, p, s = l

   return S[k:p+1].startswith(sfx)

def find_deepest(indent, s, GS, S):
   d = 0
   b = 0
   for k, p, s in s.values():
      print('%s%s%s' % ('   ' * indent, S[k:p+1], ':' if s else ''))
      if not s:
         if d == 0:
            b = k
         continue
      k1, p1 = find_deepest(indent + 1, GS[s], GS, S)
      total_len = p1 + p - k + 1
      if total_len > d:
         b = k1 - (p - k + 1)
         d = total_len
   return b, d

def longest_dup(S):
   GS = ukkonen(S + '$')
   k, p = find_deepest(0, GS[1], GS, S)
   print('FOUND: %s' % ((k, p),))
   return S[k:k+p]

print(longest_dup('banana'))
print(longest_dup('aabababaab'))
print(longest_dup('aaaaaab'))
#print(is_in('bananas', 'ananast'))
#print(is_in('aaaaaab', 'aaa'))
#print(is_in('aabababaab', 'baba'))
