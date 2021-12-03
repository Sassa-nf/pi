class Clock:
   def __init__(self):
      self.t0 = 0

   def now(self):
      return self.t0

   def tick(self, t1):
      self.t0 = t1

class Queue:
   def __init__(self, name, clock):
      self.name = name
      self.items = []
      self.waiters = []
      self.clock = clock
      self.queue_wait = 0
      self.queue_blocked = 0

   def add(self, item):
      if not self.waiters:
         self.items.append((self.clock.now(), item))
         return

      t0, thread = self.waiters.pop(0)
      self.queue_blocked += self.clock.now() - t0
      thread.resume(self.clock.now(), item)

   def take(self, thread):
      thread.suspend(self.clock.now())
      if not self.items:
         self.waiters.append((self.clock.now(), thread))
         return
      t0, item = self.items.pop(0)
      self.queue_wait += self.clock.now() - t0
      thread.resume(self.clock.now(), item)

   def __str__(self):
      return '%s: queue_wait=%.3f queue_blocked=%.3f' % (self.name, self.queue_wait, self.queue_blocked)

THREADS = {}

class Thread:
   def __init__(self, name, run_queue):
      self.name = name
      THREADS[name] = self
      self.idle = 0
      self.busy = 0
      self.run_queue = run_queue
      self.suspended_at = -1
      self.resumed_at = -1

   def resume(self, t0, item):
      self.item = item
      self.idle += t0 - self.suspended_at
      self.resumed_at = t0
      self.suspended_at = -1
      run_queue[self.name] = self

   def suspend(self, t0):
      if self.resumed_at >= 0:
         self.busy += t0 - self.resumed_at
      self.resumed_at = -1
      self.suspended_at = t0
      run_queue.pop(self.name, None)

   def __str__(self):
      return '%s: idle=%.3f busy=%.3f' % (self.name, self.idle, self.busy)

class Request:
   def __str__(self):
      return '%d' % self.rt

clock = Clock()
run_queue = {}
requests = []

db_conn1 = Thread('sock 1', run_queue)
db_conn2 = Thread('sock 2', run_queue)

conn_pool = Queue('db conn pool', clock)
conn_pool.take(db_conn1)
conn_pool.take(db_conn2)

req_queue = Queue('requests', clock)
threads = [Thread('exe %d' % i, run_queue) for i in range(5)]
for th in threads:
   req_queue.take(th)

def request():
   req = Request()
   it = new_req(req)
   it.send(None)
   it.send(it)

   req.item = it
   return req

def new_req(req):
   self = yield 0
   yield 0
   req_queue.add(self)
   req.t0 = clock.now()
   yield -1

   thread = yield 0
   thread.suspend(clock.now())
   conn_pool.add(self)
   yield -1

   sock = yield 0
   yield 10
   conn_pool.take(sock)
   thread.resume(clock.now(), self)
   yield -1

   yield 20
   thread.suspend(clock.now())
   conn_pool.add(self)
   yield -1

   sock = yield 0
   yield 10
   conn_pool.take(sock)
   thread.resume(clock.now(), self)
   yield -1

   req_queue.take(thread)
   req.rt = clock.now() - req.t0
   requests.append(req)

events = [(0, request()) for i in range(30)] + [(i, request()) for i in range(10, 20000, 10)]
while events:
   events.sort(key=lambda i: i[0])
   t0 = events[0][0]
   clock.tick(t0)
   while events and events[0][0] == t0:
      t0, t = events.pop(0)
      try:
         v = t.item.send(t)
         while v == 0:
            v = t.item.send(t)
         if v > 0:
            events.append((clock.now() + v, t))
      except:
         pass
   for k, t in {k: t for k, t in run_queue.items()}.items():
      run_queue.pop(t.name, None)
      events.append((clock.now(), t))

for th in threads:
   th.idle += clock.now() - th.suspended_at
   th.suspended_at = clock.now()

rt = 0
for r in requests:
   rt += r.rt

print('clock: %.3f' % (clock.now()))
print('RT: %.3f requests: %d' % (rt / len(requests), len(requests)))
for th in threads:
   print(th)
for q in [req_queue, conn_pool]:
   print(q)
for th in [db_conn1, db_conn2]:
   print(th)
