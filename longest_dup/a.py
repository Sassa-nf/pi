def ukkonen(S):
   # Ukkonen Suffix Tree
   S = [c for c in S]
   S.append('') # append a non-existent char

   BOTTOM = 0
   GS = [{}, {}]
   ROOT = 1
   FS = {ROOT: BOTTOM} # suffixes
   def g(s, k):
      if s is BOTTOM:
         return -1, 0, ROOT
      return GS[s].get(S[k])

   def update(s, k, i):
      s, k, r = canonize(s, k, i)
      #print('>>> UPDATE %s, %s' % (S[i] if i >= 0 else -1, (s, k, i)))
      if not r:
         return s, k
      tail = i, len(S)-1, BOTTOM # one extra char is the invalid char ''
      GS[r][S[i]] = tail
      s, k, r1 = canonize(FS[s], k, i)

      while r1:
         FS[r] = r1
         r = r1
         GS[r][S[i]] = tail
         s, k, r1 = canonize(FS[s], k, i)
      FS[r] = s
      return s, k

   def canonize(s, k, p):
      while k < p:
         k1, p1, s1 = g(s, k)
         if p1 - k1 > p - k:
            break
         k += p1 - k1
         s = s1
      return s, k, test(s, k, p)

   def test(s, k, p):
      if k >= p:
         #print('<<< TEST: k >= p in %s' % ((s, k, p, S[p]),))
         return not g(s, p) and s
      len_k = p - k
      k1, p1, s1 = g(s, k)
      if S[p] == S[k1 + len_k]:
         #print('<<< TEST: char %s is the same as at %s as per %s' % (t, k1 + len_k, ((s, k, p), (k1, p1, s1))))
         return None
      #print('<<< TEST: char %s is not the same as %s at %s as per %s' % (t, S[k1 + len_k], k1 + len_k, ((s, k, p), (k1, p1, s1))))
      r = len(GS)
      GS.append({S[k1 + len_k]: (k1 + len_k, p1, s1)})
      GS[s][S[k]] = k1, k1 + len_k, r
      #print('>>> NEW STATES: %s at %s and %s at %s' % (GS[s], s, GS[r], r))
      return r

   s = ROOT
   k = 0
   for i in range(len(S)):
      s, k = update(s, k, i)

   return GS

def print_sfx(indent, s, GS, S):
   for k, p, s in s.values():
      print('%s%s%s' % ('   ' * indent, S[k:p+1], ':' if s else ''))
      print_sfx(indent+1, GS[s], GS, S)

def is_in(S, sfx):
   GS = ukkonen(S)
   print_sfx(0, GS[1], GS, S)
   k, p, s = 0, 0, 1
   while p - k <= len(sfx):
      if not sfx.startswith(S[k:p]):
         return False
      sfx = sfx[p - k:]
      if not sfx:
         return True
      l = GS[s].get(sfx[0])
      if not l:
         return False
      k, p, s = l

   return S[k:p].startswith(sfx)

def find_deepest(indent, s, GS, S):
   d = 0
   b = 0
   for k, p, s in s.values():
      print('%s%s%s' % ('   ' * indent, S[k:p], ':' if s else ''))
      if not s:
         if d == 0:
            b = k
         continue
      k1, p1 = find_deepest(indent + 1, GS[s], GS, S)
      total_len = p1 + p - k
      if total_len > d:
         b = k1 - (p - k)
         d = total_len
   return b, d

def longest_dup(S):
   GS = ukkonen(S)
   k, p = find_deepest(0, GS[1], GS, S)
   return S[k:k+p]

print(longest_dup('banana'))
print(longest_dup('aabababaab'))
print(longest_dup('aaaaaab'))
print(is_in('bananas', 'ananast'))
print(is_in('bananas', 'ananas'))
print(is_in('bananas', 'anana'))
print(is_in('aaaaaab', 'aaa'))
print(is_in('aabababaab', 'baba'))
