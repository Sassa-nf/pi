from qrcode import qr_data, qr_code, data_layout, to_mx, qr_dub_unicode, bgnd
def htmlize(mx):
  return [''.join(['&#x%x' % ord(c) for c in r]) for r in mx]

def qr_print(mx):
  g = [u'  ', u' \u2588', u'\u2588 ', u'\u2588\u2588']
  for r in mx:
    print(':'.join([g[c >> 6]+g[(c >> 2) & 3]+'  ' for c in r]))
    print(':'.join([g[(c >> 4) & 3]+g[c & 3]+('%02x' % c) for c in r]))
    print(':'.join(['......']*11))

if __name__ == '__main__':
  s = 'otpauth://totp/ACME%20Co:john@example.com?secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=ACME%20Co&algorithm=SHA1&digits=6&period=30'
  #s = 'otpauth://totp/Menlo%20Security:mock.user@menlosecurity.com?secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=Menlo%20Security&algorithm=SHA1&digits=6&period=30'
  #s = 'otpauth://totp/Menlo%20Security:mock.user@menlosecurity.com?secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=Menlo%20Security'

  mx = to_mx(qr_code(s))
  print('\nYou may need to adjust your terminal line spacing\n\n')
  print('\n'.join(qr_dub_unicode(mx)))
  #print('<html><body>\n<span style="font-size: 10pt; line-height: 10pt;">'
  #      '<pre>\n\n\n%s</pre></span></body></html>' % '\n'.join(htmlize(qr_unicode(mx))))
  #qr_print(mx)
  #with open('screen.out', 'r') as f:
  #  mx = []
  #  for ln in f:
  #    ln = ln.decode('utf-8')[:-1]
  #    if not ln:
  #      continue
  #    mx.append([int(ln[i] != ' ') for i in xrange(4, len(ln), 2)])

  #coords = data_layout(6)
  #data = [0] * 173
  #for i in xrange(172):
  #  c = 0
  #  for j in xrange(8):
  #    x, y = coords.next()
  #    c <<= 1
  #    c |= mx[y][x] ^ bgnd(x, y)
  #  data[i] = c
  #qr_d, v = qr_data([ord(c) for c in s])
  #print('Version=%d' % v)
  #print(', '.join(['%02x' % c for c in data]))
  #print(', '.join(['%02x' % d for d in qr_d]))
