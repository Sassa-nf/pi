def longest_dup1(S):
   def find_l(l):
      i = 0
      while i + l < len(S):
         f = S[i:i+l+1]
         j = S.find(f, i + 1)
         if j >= 0:
            return f
         i += 1
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

def longest_dup2(S):
   s = [ord(c) for c in S]
   ss = [sum(s)]
   for _ in range(len(S)-1):
      l = ss[-1]
      ss = [c - s[-len(ss)] for c in ss]
      ss.append(l-s[len(ss)-1])

      l = len(S) - len(ss) + 1
      for i, v in enumerate(ss):
         f = S[i:i+l]
         for j in range(i+1, len(ss)):
            if ss[j] == v and f == S[j:j+l]:
               return f
   return ''

def longest_dup3(S):
   s = [ord(c) for c in S]
   ss = [sum(s)]
   for _ in range(len(S)-1):
      l = ss[-1]
      d = {}
      for i in range(len(ss)):
         ss[i] -= s[-len(ss) + i]
         d.setdefault(ss[i], []).append(i)

      ss.append(l-s[len(ss)-1])
      d.setdefault(ss[-1], []).append(len(ss)-1)

      l = len(S) - len(ss) + 1
      for vs in d.values():
         if len(vs) < 2:
            continue
         f = S[vs[0]:vs[0] + l]
         for j in range(1, len(vs)):
            vs[j] = S[vs[j]:vs[j]+l]
            if f == vs[j]:
               return f
         for i in range(1, len(vs)):
            f = vs[i]
            for j in range(i+1, len(vs)):
               if f == vs[j]:
                  return f
   return ''

def longest_dup4(S):
   repeats = [i for i in range(len(S)) if S.find(S[i], i+1) >= 0]
   i = 0
   l = 1
   while repeats:
      i = repeats[0]
      l += 1
      repeats = [i for i in repeats if S.find(S[i:i+l], i+1) >= 0]
   return S[i:i+l-1]

def longest_dup5(S):
   d = {'': [i for i in range(len(S))]}
   f = ''
   while d:
      d1 = {}
      f = None
      for s, js in d.items():
         f = s
         for j in js:
            if j < len(S):
               d1.setdefault(s + S[j], []).append(j+1)
      d = {k: vs for k, vs in d1.items() if len(vs) > 1}
   return f

def longest_dup6(S):
   d = {'': [(i, i) for i in range(len(S))]}
   f = ''
   while d:
      d1 = {}
      f = None
      for s, js in d.items():
         f = s
         for (i, j) in js:
            if j < len(S):
               a = d1.setdefault(s + S[j], [])
               if a and a[-1][1] == i:
                  a[-1] = a[-1][0], j + 1
               else:
                  a.append((i, j + 1))
      d = {k: vs for k, vs in d1.items() if len(vs) > 1}
   return f

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
