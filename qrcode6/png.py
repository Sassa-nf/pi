from qrcode import qr_png
import base64

with open('f.html', 'w') as f:
  s = 'otpauth://totp/Menlo%20Security:mock.user@menlosecurity.com?secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=Menlo%20Security&algorithm=SHA1&digits=6&period=30'
  png, w = qr_png(s, scale=3)
  f.write(('<html><body><img width="%dpx" height="%dpx" ' % (w, w)) +
          'src="data:image/png;base64,' + base64.b64encode(png) + '"></body></html>')
