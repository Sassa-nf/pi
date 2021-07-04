import sys
import math
from itertools import groupby

import struct
import zlib

SQRT2 = math.sqrt(2)

CELLS = 100
if len(sys.argv) > 2:
   CELLS = int(sys.argv[2])

def non_detection(d, p):
   x0, y0 = d
   x1, y1 = p
   dx = x1 - x0
   dy = y1 - y0
   v = 1 - math.exp(M * (dx * dx + dy * dy))
   return math.log(v) if v > 0 else -math.inf

def shortest_path(sums, field):
   w = len(sums[0])
   h = len(sums)
   sums[0][w // 2] = field[0][w // 2]
   paths = [[None] * w for _ in sums]
   paths[0][w // 2] = (-1, -1)
   nodes = [(w // 2, 0)]
   nn = []
   while nodes:
      x, y = nodes.pop()
      d = sums[y][x]
      f = field[y][x]
      v = d + f
      for c, r in [(c, r) for c, r in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                          if (c != x or r != y) and c >= 0 and r >= 0 and c < w and r < h]:
         if v > sums[r][c]:
            sums[r][c] = v
            paths[r][c] = (x, y)
            nn.append((c, r))
      v = d + SQRT2 * f
      for c, r in [(c, r) for c, r in [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
                          if (c != x or r != y) and c >= 0 and r >= 0 and c < w and r < h]:
         if v > sums[r][c]:
            sums[r][c] = v
            paths[r][c] = (x, y)
            nn.append((c, r))

      if not nodes:
         nn.sort()
         nodes = [k for k, g in groupby(nn)]
         nn = []

   path = [paths[-1][w // 2]]
   while path[-1] != (-1, -1):
      x, y = path[-1]
      path.append(paths[y][x])

   path.pop()
   return path

def rect(field):
   max_exp = math.log(0.3)
   return '\n'.join(['''<rect x="%f" y="%f" width="%f" height="%f" stroke="rgb(%d, 0, 0)" stroke-width="%f"/>''' %
                     (x * DX, y * DX, DX, DX, int((256 * (field[y][x] / max_exp)) if field[y][x] > max_exp else 256), DX)
                     for x in range(0, CELLS+1) for y in range(0, CELLS+1)])

detectors = []
with open(sys.argv[1]) as f:
   lines = f.readlines()
   L = float(lines[0].strip())
   M = -((math.pi / L) ** 2)
   DX = L / CELLS
   for ln in lines[2:]:
      x, y = ln.strip().split()
      detectors.append((float(x), float(y)))

field = []
for y in range(CELLS + 1):
   row = []
   field.append(row)
   for x in range(CELLS + 1):
      p = x * DX, y * DX
      row.append(sum([non_detection(d, p) for d in detectors]) * DX)

sums = [[-math.inf] * len(row) for row in field]
path = shortest_path(sums, field)

if len(sys.argv) < 3:
   print('''<svg viewBox="-1 -1 %f %f" xmlns="http://www.w3.org/2000/svg">
  %s
  <polyline stroke="yellow" stroke-width="%f" fill="none"
   points="%s"/>
  </svg><!--''' % (L+2, L+2,
               rect(field),
               DX,
               ' '.join(['%f,%f' % (x * DX, y * DX) for x, y in path])))

end_x, end_y = path[0]
print(math.exp(sums[end_y][end_x])) # we've been asked to print probability of detection, but this is the probability of non-detection - because it is near-zero

if len(sys.argv) < 3:
   print('-->')


def png(field, path):
   w = len(field)
   rw = 3 * w + 1
   img = bytearray([0] * rw * w)

   max_exp = math.log(0.3)
   for y in range(len(field)):
      row = field[y]
      for x in range(len(row)):
         img[3 * x + 1 + y * rw] = int((256 * (field[y][x] / max_exp)) if field[y][x] > max_exp else 255)
   for x, y in path:
      img[3 * x + 2 + y * rw] = 255
      img[3 * x + 3 + y * rw] = 255

   def chunk(name, bs):
      name = name.encode('us-ascii')
      return struct.pack('>I%is%isI' % (len(name), len(bs)),
                         len(bs), name, bs, zlib.crc32(name + bs) & 0xffffffff)
   return (struct.pack('>Q', 0x89504e470d0a1a0a) + # PNG signature
           chunk('IHDR', struct.pack('>IIBI', w, w, 8, 0x2000000)) + # true-colour, 8 bits per channel
           chunk('IDAT', zlib.compress(bytes(img))) +
           chunk('IEND', ''.encode('us-ascii')))

if len(sys.argv) > 3:
   with open(sys.argv[3], 'wb') as f:
      f.write(png(field, path))
