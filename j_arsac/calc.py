import sys

def parse_num(s):
   if s[0] not in '0123456789+-.' or s == '.':
      return
   try:
      d = s.lower()
      if 'e' in d or d == '+inf' or d == '-inf':
         return float(d)

      sign = -1 if d[0] == '-' else 1
      if d[0] in '+-':
         d = d[1:]
      d = d.split('.')
      if len(d) > 2 or d[-1] and d[-1][0] in '+-':
         return
      base = 10
      i = d[0]
      if d[0].startswith('0x'):
         base = 16
         i = d[0][2:]
      elif d[0].startswith('0b'):
         base = 2
         i = d[0][2:]
      elif d[0].startswith('0') and len(d[0]) > 1:
         base = 8
      i = int(i, base)
      if len(d) > 1:
         i += float(int(d[1] or '0', base)) / (base ** len(d[1]))
      if sign < 0:
         i = -i
      return i
   except:
      pass

special_forms = {
      ':': ';',
      'if': 'then',
      '<build': 'does>',
   }

reserved = {
      ':', ';', 'if', 'then', 'else', '<build', 'does>',
      '+', '-', '*', '/', '.', 'dup', 'swap', 'cr',
   }


def binary_op(f):
   def g(forth):
      op = forth.stack.pop()
      forth.stack[-1] = f(forth.stack[-1], op)
   return g

def dup(forth):
   forth.stack.append(forth.stack[-1])

def swp(forth):
   forth.stack[-1], forth.stack[-2] = forth.stack[-2], forth.stack[-1]

def cr(forth):
   print('')

def prn(forth):
   print(chr(forth.stack.pop()), end='')

built_in = {
      '+': binary_op(lambda a, b: a + b),
      '-': binary_op(lambda a, b: a - b),
      '*': binary_op(lambda a, b: a * b),
      '/': binary_op(lambda a, b: a / b),
      '.': prn,
      'dup': dup,
      'swap': swp,
      'cr': cr,
   }

class Forth:
   def __init__(self, mem, words, stack):
      self.mem = mem
      self.words = words
      self.stack = stack
      self.special_form = []
      self.defining = False

   def code(self, term):
      if self.defining and term in reserved:
         raise Exception('Uh-oh, attempting to define a reserved word ' + term)

      if term in special_forms:
         self.special_form.append([])

      if self.special_form:
         self.special_form[-1].append(term)
         t = special_forms[self.special_form[-1][0]]
         if term != t:
            return False

         t = self.special_form.pop()
         if not self.special_form:
            return self.execute(t)

         self.special_form[-1].append(t)
         return False

      return self.execute(term)

   def execute(self, term):
      if self.defining:
         if type(term) is not str:
            raise Exception('Uh-oh, attempting to define not a word ' + term)
         self.words[term] = self.stack.pop()
         self.defining = False
         return True

      if type(term) is not list:
         if type(term) is not str:
            self.stack.append(term)
            return True
         if term in reserved:
            return self.built_in(term)
         tt = self.words[term]
         if len(tt) > 1:
            self.stack.append(tt[1])
         tt = tt[0]
         return self.execute(tt)

      if type(term[0]) is str and term[0] in special_forms:
         return self.special(term)

      for t in term:
         if not self.execute(t) and not self.defining:
            raise Exception('Uh-oh, execution failed for word ' + t)
      return not self.defining

   def built_in(self, term):
      f = built_in.get(term)
      if not f:
         raise Exception('Uh-oh, no clue how to interpret built-in ' + term)
      f(self)
      return True

   def special(self, term):
      if term[0] == ':':
         if type(term[1]) != str or len(term) < 3 or term[1] in special_forms:
            raise Exception('Uh-oh, expected a word, found ' + term[1])
         if len(term) > 3 and type(term[2]) is list and term[2][0] == '<build':
            self.words[term[1]] = term[2], term[3:-1]
         else:
            self.words[term[1]] = term[2:-1],
         return True
      if term[0] == '<build':
         expr = self.stack.pop()
         self.execute(term[1:-1])
         self.stack[-1] = expr, self.stack[-1]
         self.defining = True
         return False
      if term[0] == 'if':
         i = term.find('else')
         if i < 0:
            i = -1
         if self.stack.pop() != 0:
            return self.execute(term[1:i])
         return self.execute(term[i:-1])
      raise Exception('Uh-oh, no clue how to interpret reserved word ' + term[0])

   def __str__(self):
      s = 'words:\n'
      for k, w in self.words.items():
         s += f'   {k}: {w}\n'
      s += 'stack:\n'
      for i in self.stack:
         s += f'   {i}\n'
      return s

vm = Forth(None, {}, [])

for ln in sys.stdin:
   for s in [s for s in ln.strip().split(' ') if s]:
      term = parse_num(s)
      vm.code(term if term is not None else s)

print('%s' % vm)
