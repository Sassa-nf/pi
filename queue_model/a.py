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

class Thread:
   def __init__(self, name, run_queue):
      self.name = name
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
      self.run_queue[self.name] = self

   def suspend(self, t0):
      if self.resumed_at >= 0:
         self.busy += t0 - self.resumed_at
      self.resumed_at = -1
      self.suspended_at = t0
      self.run_queue.pop(self.name, None)

   def __str__(self):
      return '%s: idle=%.3f busy=%.3f' % (self.name, self.idle, self.busy)

class Request:
   def __str__(self):
      return '%d' % self.rt

class Experiment:
   def __init__(self, thread_man):
      self.clock = Clock()
      self.run_queue = {}
      self.requests = []

      self.db_conn1 = Thread('sock 1', self.run_queue)
      self.db_conn2 = Thread('sock 2', self.run_queue)

      self.conn_pool = Queue('db conn pool', self.clock)
      self.conn_pool.take(self.db_conn1)
      self.conn_pool.take(self.db_conn2)

      self.req_queue = Queue('requests', self.clock)
      self.thread_man = thread_man
      self.threads = []

   def run(self, events, request):
      events = [(e, request(self)) for e in events]

      clock = self.clock
      run_queue = self.run_queue

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
      for th in self.threads:
         th.idle += clock.now() - th.suspended_at
         th.suspended_at = clock.now()

   def report(self):
      rt = 0
      for r in self.requests:
         rt += r.rt

      print('clock: %.3f' % (self.clock.now()))
      print('RT: %.3f requests: %d' % (rt / len(self.requests), len(self.requests)))
      for th in self.threads:
         print(th)
      for q in [self.req_queue, self.conn_pool]:
         print(q)
      for th in [self.db_conn1, self.db_conn2]:
         print(th)

def thread_man_max(max):
   count = 0
   def tm(experiment):
      nonlocal count
      if count >= max:
         return

      th = Thread('exe %d' % count, experiment.run_queue)
      count += 1
      experiment.threads.append(th)
      return th
   return tm

def request(experiment):
   req = Request()
   it = new_req(req, experiment)
   it.send(None)
   it.send(it)

   req.item = it
   return req

def new_req(req, experiment):
   clock = experiment.clock
   req_queue = experiment.req_queue
   conn_pool = experiment.conn_pool
   requests = experiment.requests

   self = yield 0
   yield 0
   if not req_queue.waiters:
      th = experiment.thread_man(experiment)
      if th:
         th.idle = clock.now()
         req_queue.take(th)

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

events = [0 for i in range(30)] + [i for i in range(10, 20000, 10)]

max_threads = 6
print('Experiment: fixed thread pool of %d threads' % max_threads)
exp = Experiment(thread_man_max(max_threads))
exp.run(events, request)
exp.report()

print('\n\n--------------------\nExperiment: unbounded thread pool')
exp = Experiment(thread_man_max(10000))
exp.run(events, request)
exp.report()


import random
import math

rnd = random.Random(42)
rate = 100
events = [0] + [-math.log(1 - rnd.random()) * 1000 / rate for _ in range(10, 20000, 10)]
for i in range(1, len(events)):
   events[i] += events[i-1]

print('\n\n--------------------\nExperiment: randomized arrival at rate %.3f, fixed thread pool of %d threads' % (rate, max_threads))
exp = Experiment(thread_man_max(max_threads))
exp.run(events, request)
exp.report()

print('\n\n--------------------\nExperiment: randomized arrival at rate %.3f, unbounded thread pool' % (rate))
exp = Experiment(thread_man_max(10000))
exp.run(events, request)
exp.report()
