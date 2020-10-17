from math import sin, cos, sqrt, pi

def sgn(a):
   return -1 if a < 0 else 1

EPSILON = 0.0000001
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
      l = sqrt(dx*dx + dy*dy)

      return l < EPSILON

   def __str__(self):
      return '<%s, %s>' % (self.x, self.y)

   def intersect(self, shape):
      if type(shape) == Point:
         if self == shape:
            return [shape]
         return []

      if type(shape) == Line:
         # the vector from the origin point is colinear
         dx = self.x - shape.p.x
         dy = self.y - shape.p.y
         l = sqrt(dx*dx + dy*dy)
         if l < EPSILON or abs(shape.v.x * dx / l + shape.v.y * dy / l) >= 1-EPSILON:
            return [self]
         return []

      if type(shape) == Circle:
         dx = self.x - shape.c.x
         dy = self.y - shape.c.y
         l = sqrt(dx*dx + dy*dy)
         if abs(l - shape.r) < EPSILON:
            return [self]
         return []

      return []

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
      self.proof = ('...', p1, p2)

   def __hash__(self):
      return self.p.__hash__() + self.v.__hash__()

   def __eq__(self, l):
      if type(l) != Line:
         return False

      # line intersecting with the origin point must be non-empty
      if not self.intersect(l.p):
         return False

      # the unit vectors are colinear:
      return abs(self.v.x * l.v.x + self.v.y * l.v.y) >= 1-EPSILON

   def __str__(self):
      return '[%s...%s]' % (self.p, self.v)

   def intersect(self, shape):
      if type(shape) == Point:
         return shape.intersect(self)

      if type(shape) == Line:
         if self == shape:
            return [self]

         if self.p == shape.p:
            return [self.p]

         l = Line(self.p, shape.p)
         l.v = Point(shape.v.x, shape.v.y, '(computed)')

         if self == l: # parallel lines
            return []

         t = ((shape.p.x - self.p.x) * self.v.y - (shape.p.y - self.p.y) * self.v.x) / (shape.v.x * self.v.y - shape.v.y * self.v.x)
         return [Point(shape.p.x + shape.v.x * t, shape.p.y + shape.v.y * t, ('^', self, shape))]

      if type(shape) == Circle:
         #    |x1  y1|
         # D =|x2  y2| = x1*y2 - x2*y1 = x1*(y1+vy) - (x1+vx)*y1 = x1*vy - vx*y1
         det = (self.p.x - shape.c.x) * self.v.y - self.v.x * (self.p.y - shape.c.y)
         discriminant = shape.r * shape.r - det * det

         if discriminant < 0:
            return []
            
         dd = sqrt(discriminant)
         p1 = Point(shape.c.x + det * self.v.y + sgn(self.v.y) * self.v.x * dd,
                    shape.c.y + (-det) * self.v.x + abs(self.v.y) * dd, ('^', self, shape))
         p2 = Point(shape.c.x + det * self.v.y - sgn(self.v.y) * self.v.x * dd,
                    shape.c.y + (-det) * self.v.x - abs(self.v.y) * dd, ('^', self, shape))
         if p1 == p2:
            return [p1]
         return [p1, p2]

      return []

class Circle:
   def __init__(self, c, r):
      global C_NAME
      self.c = Point(c.x, c.y, c.proof)
      dx = r.x - c.x
      dy = r.y - c.y

      self.r = sqrt(dx*dx + dy*dy)
      self.name = 'C_%s' % C_NAME
      C_NAME += 1
      self.proof = ('->', c, r)

   def __hash__(self):
      return self.c.__hash__() + self.r.__hash__()

   def __eq__(self, c):
      if type(c) != Circle:
         return False

      return abs(self.r - c.r) < EPSILON and self.c == c.c

   def __str__(self):
      return 'Circle(%s, %s)' % (self.c, self.r)

   def intersect(self, shape):
      if type(shape) == Point or type(shape) == Line:
         return shape.intersect(self)

      if type(shape) == Circle:
         if self == shape:
            return [shape]

         dx = shape.c.x - self.c.x
         dy = shape.c.y - self.c.y
         dd = dx*dx + dy*dy
         l = sqrt(dd)

         if l < EPSILON: # self == shape took care of approx comparison of radii and centres
            return []

         rr = shape.r*shape.r
         k = (self.r*self.r - rr + dd) / (2 * dd)
         cx = self.c.x + k * dx
         cy = self.c.y + k * dy
         line = Line(Point(cx, cy, '(computed)'), Point(cx-dy, cy+dx, '(computed)'))
         i1 = line.intersect(self)
         for p in i1:
            p.proof = ('^', self, shape)
            dx = shape.c.x - p.x
            dy = shape.c.y - p.y
            if abs(dx*dx + dy*dy - rr) > EPSILON:
               return []
         return i1

      return []

def point(p, shapes, points):
   return shapes, union(points, {p})

def line(p1, p2, shapes, points):
   intersections = {p1, p2}
   l = Line(p1, p2)
   for s in shapes:
      intersections = union(intersections, {p for p in s.intersect(l) if type(p) == Point})
   return union(shapes, {l}), union(intersections, points)

def circle(c, r, shapes, points):
   intersections = {c, r}
   circle = Circle(c, r)
   for s in shapes:
      intersections = union(intersections, {p for p in s.intersect(circle) if type(p) == Point})
   return union(shapes, {circle}), union(intersections, points)


def intersection(p, q):
   r = set()
   for s in p:
      for z in q:
         if s == z:
            r.add(s)
            break
   return r

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

def solve(shapes, points, goal, steps):
   if steps == 0:
      if intersection(goal, shapes) == goal:
         for q in shapes:
            for p in goal:
               if p == q:
                  print('%s == %s' % (p, q))
                  q.proof = ('->' + q.proof[0] + '<-', q.proof[1], q.proof[2])
                  break
         return shapes, points
      return False

   plist = list(points)
   for i in range(len(plist)):
      p1 = plist[i]
      for j in range(i):
         p2 = plist[j]
         l = Line(p1, p2)
         if l not in shapes:
            ss, pp = line(p1, p2, shapes, points)
            solution = solve(ss, pp, goal, steps-1)
            if solution:
               return solution

   for p1 in points:
      for p2 in points:
         if p1 == p2:
            continue
         c = Circle(p1, p2)
         if c not in shapes:
            ss, pp = circle(p1, p2, shapes, points)
            solution = solve(ss, pp, goal, steps-1)
            if solution:
               return solution
   return False

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
   p = set()
   for s in shapes:
      if type(s.proof) == str:
         continue
      for p1 in s.proof[1:]:
         p.add(p1)

   name = 'A'
   for p1 in p:
      p1.name = name
      name = new_name(name)

   for s in shapes:
      s.name = name
      name = new_name(name)

   for p in points:
      proof = p.proof
      if type(proof) != str:
         o, p1, p2 = proof
         proof = '%s %s %s' % (p1.name, o, p2.name)
      print('%s = %s' % (p.name, proof))

   for s in shapes:
      proof = s.proof
      if type(proof) != str:
         o, p1, p2 = proof
         proof = '%s %s %s' % (p1.name, o, p2.name)
      print('%s = %s' % (s.name, proof))

r = Point(1,0, '(given)')
c = Circle(Point(0,0, '(not given)'), r)
c.proof = '(given circle)'

p1 = Point(cos(2*pi/3), sin(2*pi/3), '(goal)')
p2 = Point(cos(-2*pi/3), sin(-2*pi/3), '(goal)')

p3 = Point(cos(3*pi/5), sin(4*pi/5), '(arbitrary)')

solution = solve({c}, {r, p3}, {Line(r, p2)}, 4)

if solution:
   print('found! %s' % (solution,))
else:
   print('not found...')

solution = solve({c}, {r, p3}, {Line(p1, p2)}, 4)

if solution:
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
