#
# Matrix solution: each denomination is a matrix that
#   can produce the number of ways to give change, given a vector
#   representing the number of ways to give change with other
#   denominations.
#
#   Then a set of two denominations is a product of their respective
#   matrices.
#
#   The whole computation is kicked off by a vector:
#   | 1 0 0 0 0 ... | - representing the case for an empty set of coins:
#                       the amount of 0 can be split in one way, all other
#                       amounts - zero ways
#   Because of this, we are really only interested in a single value in
#   the 0-th row, although to compute it, we need the whole 0-th row.
#   That's what the original solution does.
#
#   coin == 2        coin == 3
# | 1 0 1 0 ... |  | 1 0 0 1 0 0 1 ... |
# | 0 1 0 1 ... |  | 0 1 0 0 1 0 0 ... |
# | 0 0 1 0 ... |  | 0 0 1 0 0 1 0 ... |
# | 0 0 0 1 ... |  | 0 0 0 1 0 0 1 ... |
# | ...         |  | ...               |
#
# An alternative view is: matrix multiplication is associative, so we
# can split the set of coins into two, and work out the product of the
# corresponding matrices in parallel, and then compute the product of
# the resulting matrices. This is not going to be faster in this case,
# but is an important exercise from didactic point.
#
def change(amount, coins):
   def one_split(coins):
      memo = [0] * (amount + 1)
      memo[0] = 1

      for c in coins:
         for i in range(c, amount+1):
            memo[i] += memo[i-c]
      return memo
   if len(coins) < 2:
      memo = one_split(coins)
      return memo[amount]
   else:
      memo_l = one_split(coins[:len(coins) // 2]) # could kick off in parallel
      memo_r = one_split(coins[len(coins) // 2:]) # in a language where this makes sense
      memo_r.reverse() # switch from row to column to compute the value we are
      # after in the 0-th row; note reversing behaves like transpose - switches
      # the indices
      return sum([l * r for l, r in zip(memo_l, memo_r)])

print(change(5, [1, 2, 5])) # 4

print(change(500, [3,5,7,8,9,10,11])) # 35502874

print(change(200, [1, 2, 5, 10, 20, 50, 100, 200])) # euler 31: 73682
