import time

def gen_ale(a):
   def ale(x):
      return (x + a) ** 8 % 1
   return ale

ale = gen_ale(3.14159)

def ex1():
   seed = float(input('Enter the seed [0.0]: ') or 0.0)
   n = int(input('Enter the number of iterations [10000]: ') or 10000)
   counts = [0] * 50
   for _ in range(n):
      seed = ale(seed)
      counts[int(seed * 50)] += 1
   print_counts(counts)


#
#        :
#   .:  .:
# .:::_:::._
#

def print_counts(counts):
   mn, mx = min(counts), max(counts)
   if mn <= 10:
      mn = 2
   if mx > 2 and (mx - mn) % 2:
      print(''.join(['. '[min(1, mx - c)] for c in counts]))
      mx -= 1
   mx -= 1
   # assert: (mx-mn) is odd

   for m in range(mx, mn - 1, -2):
      print(''.join([' ' if c < m else '.' if c == m else ':' for c in counts]))
   if mn > 10:
      print(':' * len(counts))
      print(':' * len(counts))
      skip = '... %d ...' % (mn - 8)
      print(' ' * ((len(counts) - len(skip)) // 2), skip)
      print(':' * len(counts))
      print(':' * len(counts))
   else:
      print(''.join(['_.:'[min(c, 2)] for c in counts]))

def game1():
   score = 0
   seed = time.time() % 1
   while 1:
      rolls = int(input('How many rolls to perform? [10000]: ') or 10000)
      cheat = seed < 0.5
      seed = ale(seed)

      counts = [0] * 6
      if cheat:
         side = int(seed * 6)
         seed = ale(seed)

         prob = seed
         seed = ale(seed)
      else:
         prob = 0

      for _ in range(rolls):
         if seed < prob:
            r = side
         else:
            seed = ale(seed)
            r = int(seed * 6)

         counts[r] += 1
         seed = ale(seed)

      for m, c in zip(['[ . ]', '[. .]', '[...]', '[: :]', '[:.:]', '[:::]'], counts):
         print('%s - %6d' % (m, c))

      guess = int(input('Which side is loaded? [0 - did not cheat]: '))
      if guess == 0 and prob == 0 or prob > 0 and guess == side + 1:
         win = int(1 / (prob or 1))
         print(f'Your guess is right!\n\n*** + {win} to your score! ***')
         score += win
      else:
         print('That is not right')
         if prob > 0:
            print('%d was loaded' % (side + 1))
         else:
            print('The die was not loaded')
      if input(f'*** Your score: {score} ***\n\nTry some more? [y]') == 'n':
         break

   print(f'Thank you for trying!\nThe final score is: {score}')

def game2():
   seed = time.time() % 1

   def rnd(n=None):
      nonlocal seed
      seed = ale(seed)
      if n is None:
         return seed
      return int(seed * n)

   def player_move(total):
      score = 1 + rnd(6)
      print(f'Rolled: {score}')
      if score == 1:
         print(f'Ooops... you get 0 for this turn\nYou are left at {total}')
         return total

      if score + total >= 100:
         return score + total

      while input('Roll more? [y] ') != 'n':
         r = 1 + rnd(6)
         print(f'Rolled: {r}')
         if r == 1:
            print(f'Ooops... you get 0 for this turn\nYou are left with {total}')
            return total

         score += r
         print(f'Score is {score} now')
         if score + total >= 100:
            return score + total
      print(f'Okay, you got to {score + total}')
      return score + total

   def computer_move(total):
      score = 0
      r = 1
      while r:
         r = 1 + rnd(6)
         print(f'Rolled: {r}')
         if r == 1:
            print(f'Ooops... nothing for me\nMy score remains {total}')
            return total
         score += r

         print(f'My score is {score} now')
         if score + total >= 100:
            return score + total

         r = rnd(6)

      print(f'I am leaving it at {score + total}')
      return score + total

   print('Who goes first?')
   player = 0
   computer = 0
   if rnd(2) == 0:
      print('You do')
      player = player_move(player)

   while player < 100:
      print('My turn\n--------')
      computer = computer_move(computer)
      if computer >= 100:
         print(f'Yay! I got {computer}! I win')
         return
      print('Your turn\n--------')
      player = player_move(player)

   print(f'You got all the way to {player}\nD\'oh! you win')

