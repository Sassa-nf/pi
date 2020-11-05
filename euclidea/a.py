from math import sin, cos, sqrt, pi, tan, exp
import traceback

EPSILON = 0.0000001
EPSILON_2 = EPSILON * EPSILON
EPSILON_1 = 1-EPSILON
EPSILON_1_2 = EPSILON_1 * EPSILON_1
P_NAME = 0
L_NAME = 0
C_NAME = 0

class Point:
   def __init__(self, x, y, proof):
      global P_NAME
      self.x = x
      self.y = y
      self.name = 'P_%s' % P_NAME
      P_NAME += 1
      self.proof = proof

   def __hash__(self):
      return self.x.__hash__() + self.y.__hash__()

   def __eq__(self, p):
      if type(p) != Point:
         return False

      dx = self.x - p.x
      dy = self.y - p.y
      if dx >= EPSILON or dy >= EPSILON:
         return False

      l = sqrt(dx*dx + dy*dy)

      return l < EPSILON

   def __str__(self):
      return '<%s, %s>' % (self.x, self.y)

   def intersect(self, shape):
      if type(shape) == Point:
         if self == shape:
            return [shape]
         return []

      return shape.intersect(self)

class Line:
   def __init__(self, p1, p2):
      global L_NAME
      self.p = Point(p1.x, p1.y, p1.proof)

      dx = p2.x - p1.x
      dy = p2.y - p1.y

      l = sqrt(dx*dx + dy*dy)
      self.v = Point(dx / l, dy / l, '(computed)')

      self.name = 'L_%s' % L_NAME
      L_NAME += 1
      self.proof = ('%s ... %s', p1, p2)

   def __hash__(self):
      return self.p.__hash__() + self.v.__hash__()

   def __eq__(self, l):
      if type(l) != Line:
         return False

      return self.__eq__line(l.p, l.v)

   def __eq__line(self, l_p, l_v):
      # line intersecting with the origin point must be non-empty
      if not self.intersect(l_p):
         return False

      # the unit vectors are colinear:
      return abs(self.v.x * l_v.x + self.v.y * l_v.y) >= EPSILON_1

   def __str__(self):
      return '[%s...%s]' % (self.p, self.v)

   def intersect(self, shape):
      if type(shape) == Point:
         # the vector from the origin point is colinear
         dx = self.p.x - shape.x
         dy = self.p.y - shape.y
         dd = dx*dx + dy*dy
         if dd < EPSILON_2:
            return [shape]

         vv = self.v.x * dx + self.v.y * dy
         if vv * vv >= dd * EPSILON_1_2:
            return [shape]
         return []

      if type(shape) == Line:
         if self.__eq__line(self.p, shape.v): # parallel lines
            return [self] if self == shape else []

         if self.p == shape.p:
            return [self.p]

         t = -((shape.p.x - self.p.x) * self.v.y - (shape.p.y - self.p.y) * self.v.x) / (shape.v.x * self.v.y - shape.v.y * self.v.x)
         return [Point(shape.p.x + shape.v.x * t, shape.p.y + shape.v.y * t, ('%s ^ %s', self, shape))]

      return shape.intersect(self)

class Circle:
   def __init__(self, c, r):
      global C_NAME
      self.c = Point(c.x, c.y, c.proof)
      dx = r.x - c.x
      dy = r.y - c.y

      self.r = sqrt(dx*dx + dy*dy)
      self.name = 'C_%s' % C_NAME
      C_NAME += 1
      self.proof = ('%s -> %s', c, r)

   def __hash__(self):
      return self.c.__hash__() + self.r.__hash__()

   def __eq__(self, c):
      if type(c) != Circle:
         return False

      return abs(self.r - c.r) < EPSILON and self.c == c.c

   def __str__(self):
      return 'Circle(%s, %s)' % (self.c, self.r)

   def __intersect_line(self, shape, p_x, p_y, v_x, v_y):
      #    |x1  y1|
      # D =|x2  y2| = x1*y2 - x2*y1 = x1*(y1+vy) - (x1+vx)*y1 = x1*vy - vx*y1
      det = (p_x - self.c.x) * v_y - v_x * (p_y - self.c.y)
      discriminant = self.r * self.r - det * det

      if discriminant < 0:
         return []

      dd = sqrt(discriminant)
      c_x_det_v_y = self.c.x + det * v_y
      c_y_det_v_x = self.c.y - det * v_x
      v_x_dd = v_x * dd
      v_y_dd = abs(v_y) * dd

      p1 = Point(c_x_det_v_y + (v_x_dd if v_y >= 0 else -v_x_dd),
                 c_y_det_v_x + v_y_dd, ('%s ^ %s', self, shape))
      p2 = Point(c_x_det_v_y - (v_x_dd if v_y >= 0 else -v_x_dd),
                 c_y_det_v_x - v_y_dd, ('%s ^ %s', self, shape))
      if p1 == p2:
         return [p1]
      return [p1, p2]

   def intersect(self, shape):
      if type(shape) == Point:
         dx = shape.x - self.c.x
         dy = shape.y - self.c.y
         if abs(dx) > self.r + EPSILON or abs(dy) > self.r + EPSILON:
            return []

         dd = dx*dx + dy*dy
         if abs(dd - self.r * self.r) < EPSILON_2:
            return [shape]
         return []

      if type(shape) == Line:
         return self.__intersect_line(shape, shape.p.x, shape.p.y, shape.v.x, shape.v.y)

      if type(shape) == Circle:
         if self == shape:
            return [shape]

         dx = shape.c.x - self.c.x
         dy = shape.c.y - self.c.y
         dd = dx*dx + dy*dy

         rr = shape.r*shape.r
         rR = self.r*self.r
         two_r = 2 * self.r * shape.r

         if dd < rr + rR - two_r + EPSILON: # self == shape took care of approx comparison of radii and centres
            # the centres are closer to each other than is needed for circles to overlap:
            # |r - R| is the distance between the centres when the circles touch; otherwise one circle is
            # fully inside the other
            return []

         if dd > rr + rR + two_r + EPSILON:
            return []

         l = sqrt(dd)
         #dx = dx / l
         #dy = dy / l

         k = (rR - rr + dd) / (2 * dd)
         cx = self.c.x + k * dx
         cy = self.c.y + k * dy

         i1 = self.__intersect_line(shape, cx, cy, -dy / l, dx / l)
         for p in i1:
            dx = shape.c.x - p.x
            dy = shape.c.y - p.y
            if abs(dx*dx + dy*dy - rr) > EPSILON:
               return []
         return i1

      return shape.intersect(self)

def point(p, shapes, points):
   return {}, union(points, {p})

def line(p1, p2, shapes, points):
   l = Line(p1, p2)
   if included(l, shapes):
      return None, points

   intersections = {p1, p2}
   for s in shapes:
      intersections = union(intersections, {p for p in s.intersect(l) if type(p) == Point})
   return l, union(intersections, points)

def circle(c, r, shapes, points):
   circle = Circle(c, r)
   if included(circle, shapes):
      return None, points

   intersections = {c, r}
   for s in shapes:
      intersections = union(intersections, {p for p in s.intersect(circle) if type(p) == Point})
   return circle, union(intersections, points)


def intersection(p, q):
   r = set()
   not_r = set()
   for s in p:
      found = False
      for z in q:
         if s == z:
            found = True
            break
      (r if found else not_r).add(s)
   return r, not_r

def union(p, q):
   r = set(p)
   for z in q:
      found = False
      for s in p:
         if z == s:
            found = True
            break
      if not found:
         r.add(z)
   return r

def included(s, shapes):
   for ss in shapes:
      if ss == s:
         return True

   return False

def solve(shapes, points, goal, steps):
   for solution in solve_it(shapes, points, goal, steps):
      return solution

   return False

def solve_it(shapes, points, goal, steps):
   if len(goal) > steps:
      g1, goal = intersection(goal, shapes)

   if not goal:
      yield shapes, points
      return

   if steps == 0:
      return

   plist = list(points)
   for i in range(len(plist)):
      p1 = plist[i]
      for j in range(i):
         p2 = plist[j]
         ss, pp = line(p1, p2, shapes, points)
         if not ss:
            continue

         if len(goal) < steps:
            g1, g2 = None, goal
         else:
            g1, g2 = intersection(goal, {ss})
         if len(g2) > steps:
            continue
         if g1:
            ss.proof = (ss.proof[0] + ' (goal)', ss.proof[1], ss.proof[2])
         yield from solve_it(union(shapes, {ss}), pp, g2, steps-1)

   if len(goal) == steps and not [s for s in goal if type(s) == Circle]:
      return

   for p1 in points:
      for p2 in points:
         if p1 == p2:
            continue
         ss, pp = circle(p1, p2, shapes, points)
         if not ss:
            continue

         if len(goal) < steps:
            g1, g2 = None, goal
         else:
            g1, g2 = intersection(goal, {ss})
         if len(g2) > steps:
            continue
         if g1:
            ss.proof = (ss.proof[0] + ' (goal)', ss.proof[1], ss.proof[2])
         yield from solve_it(union(shapes, {ss}), pp, g2, steps-1)
   return

def new_name(name):
   if name[0] == 'Z':
      if len(name) == 1:
         name = name + '0'
      name = 'A%s' % (int(name[1:]) + 1)
   else:
      name = chr(ord(name[0])+1) + name[1:]

   return name

def print_solution(solution):
   shapes, points = solution
   ps = set()
   for s in shapes:
      if type(s.proof) == str:
         continue
      for p1 in s.proof[1:]:
         ps.add(p1)

   name = 'A'
   for p1 in ps:
      p1.name = name
      name = new_name(name)

   for s in shapes:
      s.name = name
      name = new_name(name)

   for p in ps:
      proof = p.proof
      if type(proof) != str:
         o, p1, p2 = proof
         proof = o % (p1.name, p2.name)
      print('%s = %s' % (p.name, proof))

   for s in shapes:
      proof = s.proof
      if type(proof) != str:
         o, p1, p2 = proof
         proof = o % (p1.name, p2.name)
      print('%s = %s' % (s.name, proof))

o = Point(0, 0, '(given)')
o1 = Point(pi, 0, '(given)')
o2 = Point(1, exp(1), '(given)')
ll = Line(o, o1)
lr = Line(o, o2)
ll.proof = ('%s ... %s (given)', o, o1)
lr.proof = ('%s ... %s (given)', o, o2)

for pl in [Line(o2, o), Line(o, o2)]:
  for rl in [Line(o1, o2), Line(o2, o1)]:
     for (pp,) in [rl.intersect(pl), pl.intersect(rl)]:
        if pp != o2:
           print('uh-oh: %s ^ %s == %s != %s' % (pl, rl, pp, o2))

o3 = Point(1+pi, exp(1), '(goal)')
solution = False
for shapes, points in solve_it({ll, lr}, {o, o1, o2}, {Line(o1, o3)}, 5):
   solution = solve(shapes, points, {Line(o2, o3)}, 1)
   if solution:
      break
#solution = solve({ll, lr}, {o, o1, o2}, {Line(o1, o3), Line(o2, o3)}, 6)

if solution:
   print('Building a parallelogram:')
   print_solution(solution)
else:
   print('not found...')

r = Point(1,0, '(given)')
o = Point(0, 0, '(arbitrary)')
o1 = Point(r.x, (r.x-o.x) * tan(pi/12), '(goal)')
ll = Line(o, r)
solution = solve({ll}, {r, o}, {Line(o, o1)}, 5)

if solution:
   print('Building a 15 degree angle:')
   print_solution(solution)
else:
   print('not found...')

c = Circle(Point(0,0, '(not given)'), r)
c.proof = '(given circle)'

p1 = Point(cos(2*pi/3), sin(2*pi/3), '(goal)')
p2 = Point(cos(-2*pi/3), sin(-2*pi/3), '(goal)')

p3 = Point(cos(4*pi/5), sin(4*pi/5), '(arbitrary)')

pp, = c.intersect(p3)
print('%s ^ %s == %s, %s' % (p3, c, pp, pp == p3))
print('%s, %s, %s' % (r, p1, p2))

solution = False
for shapes, points in solve_it({c}, {r, p3}, {Line(p1, r)}, 4):
   for shapes, points in solve_it(shapes, points, {Line(r, p2)}, 1):
      solution = solve(shapes, points, {Line(p2, p1)}, 1)
      if solution:
         break
   if solution:
      break

if solution:
   print('Building an equilateral triangle:')
   print_solution(solution)
else:
   print('not found...')

c1 = Circle(r, p3)
c2 = Circle(p3, r)
pp1, pp2 = c1.intersect(c)
pp3, pp4 = c2.intersect(c)
pp5, pp6 = c2.intersect(c1)
print('p3: %s\npp1: %s\npp2: %s\npp3: %s\npp4: %s\npp5: %s\npp6: %s' % (p3, pp1, pp2, pp3, pp4, pp5, pp6))

#
# p3: <-0.8090169943749473, 0.5877852522924732>
# pp1: <-0.8090169943749472, 0.5877852522924735>
# pp2: <-0.8090169943749472, -0.5877852522924735> <- ...
# pp3: <1.0000000000000004, 0>    -- 9.43689570931383e-16>
# pp4: <0.3090169943749464, -0.9510565162951543>  <- ...
# pp5: <0.6045284632676539, 1.8605472991527119>
# pp6: <-0.41354545764260064, -1.272762046860239> <- ...
#
c3 = Circle(pp6, pp2)
pp7, pp8 = c3.intersect(c2)
print('%s, %s: %s' % (Line(r, pp7), Line(r, pp8), Line(pp8, r) == Line(r, p2)))

p4 = Point(cos(-2*pi/3), sin(-2*pi/2) - 1, '(given)')
p5 = Point(cos(2*pi/3), sin(2*pi/3) + 1, '(given)')

p6 = Point(2*cos(2*pi/3)+1, 0, '(given)')
c1 = Circle(Point(p6.x-1, 0, '(given)'), p6)

print('points: %s' % (c.intersect(Line(p5, p4)) == [p1, p2]))
print('points: %s' % (c.intersect(c1) == [p1, p2]))



# A = (given)
# C = (given)
# D = (given)
# H = A ... D (given)
# I = A ... C (given)

# J = A -> D
# G = H ^ J

# B = I ^ J
# K = D ... B

# L = C -> B

# E = K ^ L
# M = E ... C (goal)

# N = B -> G
# F = J ^ N
# O = D ... F (goal)
