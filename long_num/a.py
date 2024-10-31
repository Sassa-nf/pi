# find the smallest natural number greater than 0 such that moving the
# last digit to the first position makes the number N times bigger
#
# eg 421052631578947368 * 2 -> 842105263157894736

def find_num(n, x):
  seen = set()
  ds = []
  d = x
  while d not in seen:
    seen.add(d)
    carry = d // 10
    d = d % 10
    ds = [d] + ds
    d = n * d + carry

  # found a loop, now the number is going to get only longer
  # by replicating the loop; if the loop does not contain x,
  # then the number will never start with x after multiplying
  # by n; if the loop does contain x, then it stops at the
  # first occurrence of x - exactly when the number fits the
  # requirement

  num = 0
  for i in ds:
    num = num * 10 + i

  return ds, num, d == x and carry != x # found a loop, and it is looped to x, and the number does not start with 0; this is the same as num * n == (i * (10 ** (len(ds) - 1))) + num // 10

for n in range(2, 10):
  print("now looking for numbers for %d" % n)
  max_ds = [0]
  min_n = 0
  for i in range(10):
    ds, num, b = find_num(n, i)
    if b and (max_ds[0] == 0 or num < min_n):
      max_ds = ds
      min_n = num
    print((ds, num, b))

  if max_ds[0] == 0:
    print("no solution for %d" % n)
  else:
    print("solution for %d: %d" % (n, min_n))
