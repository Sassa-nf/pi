def inplace(xs):
   i, r, w = 0, 0, len(xs)-1
   while i <= w:
      if xs[i] == 2:
         xs[i] = xs[w]
         xs[w] = 2
         w -= 1
         continue

      if xs[i] == 0:
         xs[i] = 1
         xs[r] = 0
         r += 1
      i += 1

doh = [2,0,2,1,1,0]
inplace(doh)
print(doh)
