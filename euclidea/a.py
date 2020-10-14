from math import sin, cos, sqrt, pi

def sgn(a):
   return -1 if a < 0 else 1

EPSILON = 0.001
class Point:
   def __init__(self, x, y):
      self.x = x
      self.y = y

   def __hash__(self):
      return self.x.__hash__() + self.y.__hash__()

   def __eq__(self, p):
      if type(p) != Point:
         return False

      dx = self.x - p.x
      dy = self.y - p.y
      l = sqrt(dx*dx + dy*dy)

      return l < EPSILON

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
      self.p = Point(p1.x, p1.y)

      dx = p2.x - p1.x
      dy = p2.y - p1.y

      l = sqrt(dx*dx + dy*dy)
      self.v = Point(dx / l, dy / l)

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

   def intersect(self, shape):
      if type(shape) == Point:
         return shape.intersect(self)

      if type(shape) == Line:
         if self == shape:
            return [self]

         if self.p == shape.p:
            return [self.p]

         l = Line(self.p, shape.p)
         l.v = Point(shape.v.x, shape.v.y)

         if self == l: # parallel lines
            return []

         t = ((shape.p.x - self.p.x) * self.v.y - (shape.p.y - self.p.y) * self.v.x) / (shape.v.x * self.v.y - shape.v.y * self.v.x)
         return [Point(shape.p.x + shape.v.x * t, shape.p.y + shape.v.y * t)]

      if type(shape) == Circle:
         #    |x1  y1|
         # D =|x2  y2| = x1*y2 - x2*y1 = x1*(y1+vy) - (x1+vx)*y1 = x1*vy - vx*y1
         det = (self.p.x - shape.c.x) * self.v.y - self.v.x * (self.p.y - shape.c.y)
         discriminant = shape.r * shape.r - det * det

         if discriminant < 0:
            return []
            
         dd = sqrt(discriminant)
         p1 = Point(shape.c.x + det * self.v.y + sgn(self.v.y) * self.v.x * dd,
                    shape.c.y + (-det) * self.v.x + abs(self.v.y) * dd)
         p2 = Point(shape.c.x + det * self.v.y - sgn(self.v.y) * self.v.x * dd,
                    shape.c.y + (-det) * self.v.x - abs(self.v.y) * dd)
         if p1 == p2:
            return [p1]
         return [p1, p2]

      return []

class Circle:
   def __init__(self, c, r):
      self.c = Point(c.x, c.y)
      dx = r.x - c.x
      dy = r.y - c.y

      self.r = sqrt(dx*dx + dy*dy)

   def __hash__(self):
      return self.c.__hash__() + self.r.__hash__()

   def __eq__(self, c):
      if type(c) != Circle:
         return False

      return abs(self.r - c.r) < EPSILON and self.c == c.c

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
         k = (self.r*self.r - rr + dd) / (2 * l)
         cx = self.c.x + k * dx
         cy = self.c.y + k * dy
         line = Line(Point(cx, cy), self.c)
         line.v = Point(-dy / l, dx / l)
         i1 = line.intersect(self)
         for p in i1:
            dx = shape.c.x - p.x
            dy = shape.c.y - p.y
            if abs(dx*dx + dy*dy - rr) > EPSILON:
               return []
         return i1

      return []

def point(p, shapes, points):
   return shapes, points.union({p})

def line(p1, p2, shapes, points):
   intersections = set()
   l = Line(p1, p2)
   for s in shapes:
      intersections = intersections.union({p for p in s.intersect(l) if type(p) == Point})
   return shapes.union({l}), intersections.union(points).union({p1, p2})

def circle(c, r, shapes, points):
   intersections = set()
   circle = Circle(c, r)
   for s in shapes:
      intersections = intersections.union({p for p in s.intersect(circle) if type(p) == Point})
   return shapes.union({circle}), intersections.union(points).union({c, r})


def solve(shapes, points, goal, steps):
   if steps == 1:
      for g in goal:
         found = False
         for s in shapes:
            if s == g:
               found = True
               break
         if not found:
            return False
      return True

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

r = Point(1,0)
c = Circle(Point(0,0), r)

p1 = Point(cos(2*pi/3), sin(2*pi/3))
p2 = Point(cos(-2*pi/3), sin(-2*pi/3))

p3 = Point(cos(4*pi/5), sin(4*pi/5))

solution = solve({c}, {r, p3}, {Line(r, p2)}, 4)

if solution:
   print('found! %s' % (solution,))
else:
   print('not found...')

p4 = Point(cos(-2*pi/3), sin(-2*pi/2) - 1)
p5 = Point(cos(2*pi/3), sin(2*pi/3) + 1)

p6 = Point(2*cos(2*pi/3)+1, 0)
c1 = Circle(Point(p6.x-1, 0), p6)

print('points: %s' % (c.intersect(Line(p5, p4)) == [p1, p2]))
print('points: %s' % (c.intersect(c1) == [p1, p2]))
