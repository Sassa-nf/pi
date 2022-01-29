from binascii import crc32

def longest_dup(S):
   S = bytes(S, 'ascii')
   crcs = {ord(c): crc32(bytes(c, 'ascii'), 0xffffffff) for c in 'abcdefghijklmnopqrstuvwxyz'}

   def find_l(l):
      if not l:
         return None

      nulls = b'\x00' * l
      chars = {c: crc32(nulls, crc) ^ 0xffffffff for c, crc in crcs.items()}
      s = crc32(S[:l], 0xffffffff)
      sums = {s: [0]}
      j = 0
      for i in range(l, len(S)):
         s = crc32(S[i:i+1], s) ^ chars[S[j]]
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
   f = b''
   while begin < end:
      i = (begin + end) // 2
      ff = find_l(i)
      if ff:
         f = ff
         begin = i + 1
      else:
         end = i
   return f.decode('ascii')
print(longest_dup('banana'))

print('%x' % crc32(b'anana', 0xffffffff))
cb = bytearray(b'b')
nulls = b'\x00' * 5
b = crc32(nulls, crc32(b'b', 0xffffffff)) ^ 0xffffffff
print('%x' % (crc32(b'banana', 0xffffffff) ^ b))

print('%x' % (crc32(b'a', crc32(b'banan', 0xffffffff)) ^ b))
