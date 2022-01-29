from a import reconstructQueue, reconstructQueueHint
from random import randrange
from timeit import default_timer as timer

def shuffle(q):
   for i in range(1, len(q)):
      j = randrange(i)
      q[j], q[i] = q[i], q[j]
   return q

def gen_queue(sz):
   q = shuffle(list(range(sz-1)))
   q.append(q[-1])
   q = shuffle(q)
   for i in range(len(q)):
      q[i] = (q[i], sum([int(p[0] >= q[i]) for p in q[:i]]))
   return q

def test_q(r, q):
   global timing
   p = shuffle(list(q))
   t0 = timer()
   p = r(p)
   t1 = timer()
   timing += t1 - t0
   return q if p != q else []

timing = 0

test_q(reconstructQueue, gen_queue(1100))
print(timing)

#for sz in range(5, 150):
#   timing = 0.0
#   for _ in range(1000):
#      q = test_q(reconstructQueueHint, gen_queue(sz))
#      if q:
#         print('UH-OH: %s' % q)
#         break
#   print('%s %s' % (sz, timing))
