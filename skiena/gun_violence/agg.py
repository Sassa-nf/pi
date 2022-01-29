stats={}

def read_csv(stats, fn):
   name=fn[:fn.rindex('_')]
   with open(fn) as f:
      skip = True
      for ln in f:
         if skip:
            if 'Region' in ln:
               skip = False
            continue
         quoted=ln.strip().split('"')
         ln = ''.join([s if i % 2 == 0 else s.replace(',', '') if s[0] in '123456789' else s.replace(',', ';') for s, i in zip(quoted, range(len(quoted)))])
         ln = ln.split(',')
         if not ln[-1]:
            continue
         ln[1] = ln[1].replace('ern', '')
         if ln[2] not in stats:
            stats[ln[2]] = {'region': ln[0], 'subregion': ln[1]}
         s = stats[ln[2]]
         if s['region'] != ln[0] or s['subregion'] != ln[1]:
            print('Country: %s attributed to %s and %s, %s and %s in %s' % (ln[2], s['region'], ln[0], s['subregion'], ln[1], fn))
         s[name] = float(ln[-1])

with open('homicides.csv') as h, \
     open('gun_avail') as g:
   skip = True
   for ln in g:
      if 'United States' in ln:
         skip = False
      elif skip:
         continue
      ln = ln.strip().split('\t')
      ln[4] = ln[4].replace('ern', '')
      stats[ln[1].strip()] = {'region': ln[3], 'subregion': ln[4], 'guns': float(ln[2]), \
                              'serious_assault': -1, 'kidnapping': -1, 'robbery': -1}
   skip = True
   for ln in h:
      if 'Afghanistan' in ln:
         skip = False
      elif skip:
         continue
      ln = ln.strip().split(',')
      ln[2] = ln[2].replace('ern', '')
      if ln[-1] not in stats:
         stats[ln[-1]] = {'region': ln[1], 'subregion': ln[2]}
      s = stats[ln[-1]]
      if s['region'] != ln[1] or s['subregion'] != ln[2]:
         print('Country: %s attributed to %s and %s, %s and %s' % (ln[-1], s['region'], ln[1], s['subregion'], ln[2]))
      s['homicides'] = float(ln[0])

   read_csv(stats, 'serious_assault_0.csv')
   read_csv(stats, 'kidnapping_0.csv')
   read_csv(stats, 'robbery_0.csv')

print('Country,Region,Subregion,Guns,Homicides,Serious Assault,Robbery,Kidnapping')
for c, s in stats.items():
   if not all([i in s for i in ['kidnapping', 'robbery', 'serious_assault', 'homicides', 'guns']]):
      continue
   s['country'] = c
   print('%(country)s,%(region)s,%(subregion)s,%(guns).3f,%(homicides).3f,%(serious_assault).3f,%(robbery).3f,%(kidnapping).3f' % s)
