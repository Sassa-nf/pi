from functools import reduce

def minSum(arr, target):
   def step(a, x):
      b, e, s = a[-1]
      if x < 0:
         a[-1] = (e+1, e+1, 0)
      else:
         s += x
         while s > target:
            s -= arr[b]
            b += 1
         a[-1] = (b, e+1, s)
         if s == target:
            a.append((b+1, e+1, s - arr[b]))
      return a
   r = reduce(step, arr, [(0, 0, 0)])
   r.pop()

   if len(r) < 2:
      return -1

   found = None
   min_l0 = None
   for i, v in enumerate(r):
      b, e, _ = v
      l0 = e - b
      if min_l0 and l0 >= min_l0:
         continue
      min_l0 = l0
      for j in range(i+1, len(r)):
         if r[j][0] >= e:
            w = min(r[j:], key=lambda w: w[1] - w[0])
            l1 = w[1] - w[0]
            if found is None or found > l0 + l1:
               found = l0 + l1
            break
         
   return -1 if found is None else found

print(minSum([3,2,2,4,3], 3))
print(minSum([7,3,4,7], 7))
print(minSum([4,3,2,6,2,3,4], 6))
print(minSum([5,5,4,4,5], 3))
print(minSum([3,1,1,1,5,1,2,1], 3))

i = [78,18,1,94,1,1,1,29,58,3,4,1,2,56,17,19,4,1,63,2,16,11,1,1,2,1,25,62,10,69,12,7,1,6,2,92,4,1,61,7,26,1,1,1,67,26,2,2,70,25,2,68,13,4,11,1,34,14,7,37,4,1,12,51,25,2,4,3,56,21,7,8,5,93,1,1,2,55,14,25,1,1,1,89,6,1,1,24,22,50,1,28,9,51,9,88,1,7,1,30,32,18,12,3,2,18,10,4,11,43,6,5,93,2,2,68,18,11,47,33,17,27,56,13,1,2,29,1,17,1,10,15,18,3,1,86,7,4,16,45,3,29,2,1,1,31,19,18,16,12,1,56,4,35,1,1,36,59,1,1,16,58,18,4,1,43,31,15,6,1,1,6,49,27,12,1,2,80,14,2,1,21,32,18,15,11,59,10,1,14,3,3,7,15,4,55,4,1,12,4,1,1,53,37,2,5,72,3,6,10,3,3,83,8,1,5]
t = 97

print(minSum(i, t))

