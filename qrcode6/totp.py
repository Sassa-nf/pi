import base64
import hmac
import hashlib


def totp(fhash=hashlib.sha1, dt=30.0, digits=6):
  """Produce a function that supports TOTP protocol given a hashlib hash
  function, time step, and the number of digits.
  
  The defaults are set for Google Authentication, with time step fixed to
  30 seconds, hash function set to SHA1, and the number of digits limited
  to 6.
  
  Pass the key for HMAC and the timestamp offset from Unix epoch to the
  function returned."""
  mod = 10 ** digits
  def auth(k, t):
    ts = int(t / dt)
    s = ''.join([chr((ts >> j) & 0xff) for j in xrange(56, -1, -8)])
    hm = hmac.new(k, s, fhash)
    dig = hm.digest()
    off = ord(dig[-1]) & 0xf
    hashint = reduce(lambda a, c: (a << 8) | ord(c), dig[off:off+4], 0)
    return (hashint & 0x7fffffff) % mod

  return auth

googleauth = totp()
