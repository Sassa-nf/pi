# find the smallest natural number greater than 0 such that moving the
# last digit to the first position makes the number N times bigger
#
# eg 421052631578947368 * 2 -> 842105263157894736

def find_num(n, x):
  d = n * x
  carry = d // 10
  d = d % 10
  ds = [x]
  while d != x or carry != 0:
    ds = [d] + ds
    d = n * d + carry
    carry = d // 10
    d = d % 10

  num = 0
  for i in ds:
    num = num * 10 + i

  return ds, num, num * n == (i * (10 ** (len(ds) - 1))) + num // 10

for n in range(2, 10):
  print("now looking for numbers for %d" % n)
  max_ds = [0]
  min_n = 0
  for i in range(10):
    ds, num, b = find_num(n, i)
    if max_ds[0] == 0 or num < min_n and ds[0] != 0:
      max_ds = ds
      min_n = num
    print((ds, num, b))

  if max_ds[0] == 0:
    print("no solution for %d" % n)
  else:
    print("solution for %d: %d" % (n, min_n))
