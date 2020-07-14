from a import ukkonen, find_deepest

def print_sfx(indent, s, GS, S):
   for k, p, s in s.values():
      print('%s%s%s' % ('   ' * indent, S[k:p], ':' if s else ''))
      print_sfx(indent+1, GS[s], GS, S)

# ukkonen_tree produces an array of triplets (k, p, a) of length O(N):
# - k: the starting position of a substring
# - p: the position after the end of substring
# - a: action on mismatch at any position between k and p:
#   a <= 0: -a the length of the boundary that matches
#   a > 0: a is the index of where to restart matching
def ukkonen_tree(b):
   GS = ukkonen(b)
   states = []
   find_boundary(0, GS[1], GS, b, 0, 0, states)
   return states

def find_boundary(indent, s, GS, S, longest_sfx, total_len, states):
   prev = None
   for k, p, s in s.values():
      if prev: # link up siblings
         prev[-1] = len(states)
      prev = [k, k+1 if p > k else k, -longest_sfx]
      states.append(prev)
      if p - k > 1: # substrings that are longer than 1 have no siblings after the first char
                    # they end up reporting just the longest suffix
         states.append([k+1, p, -longest_sfx])
      if p >= len(S): # substrings that run to the end of S have an artificial empty suffix
         states.append([p, p, -(total_len + p - k)])

      print('%d %d %s%s%s' % (longest_sfx, k, '   ' * indent, S[k:p] or '$', ':' if s else ''))
      new_len = total_len + p - k
      find_boundary(indent+1, GS[s], GS, S,
                    new_len if '' in GS[s] else longest_sfx, new_len, states)

def match_boundary(b, bs, text):
   # the position from which started looking back
   match = len(b)-1

   # current position
   i = match

   # current state
   curr = 0
   k, p, a = bs[curr]
   while i < len(text):
      print('@%d: matching %s and %s' % (i, text[i:match+1][::-1], b[k:p]))
      if match - i == len(b):
         print('matched fully')
         return i + 1, len(b)

      if k < len(b) and text[i] == b[k]:
         k += 1
         i -= 1
         if k < p:
            continue
         # successfully matched to the end of a substring, switch to the next substring
         curr += 1
         report = 'substring matched'
      elif a > 0:
         # assert: a single character mismatched, switch to the next choice
         curr = a
         report = 'mismatch'
      else:
         # a <= 0;
         # -a is the longest suffix; len(b) + a is the length of the unmatched remainder
         match += len(b) + a
         i = match
         curr = 0
         report = 'matched partially; move on to position: %s' % (match)
      k, p, a = bs[curr]
      print('%s; switched to %d now: %s, %s, %s' % (report, curr, k, p, a))
   return -1, 0

      

b = 'anbancanca'
print('\n'.join(['%d: %s %d' % (i, b[k:p], a) for i, (k, p, a) in enumerate(ukkonen_tree(b))]))


bs = ukkonen_tree(b)
txt = 'anandohdohbla' + b[::-1] + 'nana-- doh'
m, l = match_boundary(b, bs, txt)
print('%d: %s + %s + %s' % (m, txt[:m], txt[m: m + l], txt[m+l:]))
