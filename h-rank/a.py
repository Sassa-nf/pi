def hIndex(citations):
   N = len(citations)
   begin, end = 0, N
   h = 0
   while begin < end:
      i = (begin + end) // 2
      hh = N - i
      if citations[i] >= hh:
         h = hh
         end = i
      else:
         begin = i + 1
   return h

print(hIndex([0,1,3,5,6]))
print(hIndex([100]))
print(hIndex([11, 12]))
print(hIndex([0, 0, 1]))
