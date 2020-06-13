def change(amount, coins):
   memo = [0] * (amount + 1)
   memo[0] = 1

   for c in coins:
      for i in range(c, amount+1):
         memo[i] += memo[i-c]
   return memo[amount]

print(change(5, [1, 2, 5]))

print(change(500, [3,5,7,8,9,10,11]))
