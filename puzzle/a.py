
words = {}

with open('words_4.txt') as f:
   for ln in f:
      words[ln.strip()] = 1

def search(words, w):
   for k in words:
      if sum([x == y for x, y in zip(k, w)]) == 3:
         yield k

w1=['shoe', 'shod', 'shed', 'sled', 'seed', 'heed']
w2=['show', 'slow', 'glow', 'grow', 'brow']

for w in w1:
  del words[w]
for w in w2:
  del words[w]
print(list(search(words, w1[-1])))
