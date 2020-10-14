import time
from pygame import mixer
mixer.init()

files = """Ah.wav Dd.wav Ff.wav I.wav Mm.wav Sh.wav Xx.wav b.wav e.wav g.wav ih.wav l.wav n.wav p.wav r.wav t.wav v.wav x.wav z.wav Ch.wav Ee.wav Gh.wav Ll.wav Ou.wav Uh.wav a.wav d.wav f.wav h.wav k.wav m.wav o.wav q.wav s.wav u.wav w.wav y.wav""".split(' ')

ss = {f[0]: mixer.Sound(f) for f in files}

def say(that):
   for s in that:
      if s in ss:
         ss[s].play()
         sleep = ss[s].get_length()
      else:
         sleep = 0.2
      time.sleep(sleep)
