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
         r1 = len(GS)
         GS.append({})
         GS[r][S[i]] = i, len(S) - 1, r1 # originally: GS[r][S[i]] = i, len(S), r
         FS[r1] = BOTTOM                 # originally: not linked
         #print('>>> NEW STATE: %s at %s' % (GS[r], r))
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

   return [GS, FS]

def is_in(S, sfx):
   GS, FS = ukkonen(S)
   print('GS: %s' % GS)
   print('FS: %s' % FS)
   k, p, s = 0, -1, 1
   while p - k < len(sfx):
      print('<<< %s ~ %s %s %s' % (sfx, S[k:p+1], (k, p, s), GS[s]))
      if not sfx.startswith(S[k:p+1]):
         return False
      sfx = sfx[p - k + (1 if p < len(S) else 0):]
      print('<<< TRIMMED TO %s' % (sfx,))
      if not sfx:
         return True
      if s != 1:
         s = FS[s]
      l = GS[s].get(sfx[0])
      if not l:
         print('<<< %s ~ %s %s %s' % (sfx, s, l, GS[s]))
         return False
      k, p, s = l

   return S[k:p+1].startswith(sfx)

def longest_dup(S):
   return ukkonen(S)

#print(longest_dup('banana'))
print(is_in('bananas', 'anana'))
