# Given a matrix of cells, work out the max number of coins you can collect by starting
# by going down from the top left corner.
#
# The cells may have '.' (empty), '*' (coin), '>' (force to go right), 'v' (force to go
# down). You may rotate each row to align better with the vertical move from the previous
# row.
#
# e.g.
#
# >**     *>*
# *>*  => *>* = 4 coins; first go down until the last row, where we switch to go right,
# **>     >**            and after collecting 2 coins, we wrap around and keep going right forever.

from typing import List

def getMaxCollectableCoins(R: int, C: int, G: List[List[str]]) -> int:
   m = 0
   while G:
      m = max_coins(m, G.pop())

   return m

def max_coins(m, row):
   row = ''.join(row)
   if row == '>' * len(row):
      return 0
   coins = sum([1 for c in row if c == '*'])
   just_down = m + (coins > 0)
   if '>' not in row:
      return just_down
   if 'v' not in row or coins == 1:
      return max(just_down, coins)

   i = row.index('v')
   row = (row[i+1:] + row[0:i]).split('v')
   max_horz = max([sum([1 for c in c[c.index('>'):] if c == '*']) for c in row if '>' in c])
   return max(just_down, m + max_horz)

print(getMaxCollectableCoins(1, 1, [[c for c in r] for r in '.*** **v> .*..'.split()]), 4)
print(getMaxCollectableCoins(1, 1, [[c for c in r] for r in '>** *>* **>'.split()]), 4)
print(getMaxCollectableCoins(1, 1, [[c for c in r] for r in '>> **'.split()]), 0)
print(getMaxCollectableCoins(1, 1, [[c for c in r] for r in '>*v*>* *v*v>* .*>..* .*..*v'.split()]), 6)
