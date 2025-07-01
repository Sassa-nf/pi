import argparse
import subprocess
import base64
import getpass
import json
import sys
import time

def aes_decrypt(key, text):
   """Decrypt text with AES"""
   iv, text = text[:16], text[16:]

   r = subprocess.run(['openssl', 'aes-256-cbc' if len(key) == 32 else 'aes-128-cbc',
                       '-d',
                       '-nosalt',
                       '-iv', iv.hex(),
                       '-K', key.hex()],
                       input=text,
                       capture_output=True)
   if r.stderr:
      print(r.stderr.decode('ascii'))
   return r.stdout

def aes_encrypt(key, text):
   """Encrypt text with AES"""
   block_size = len(key)
   pad_len = block_size - len(text) % block_size
   pad_char = chr(pad_len)
   pad = pad_len * pad_char
   rnd = open('/dev/random', 'rb')
   iv = rnd.read(block_size)
   r = subprocess.run(['openssl', 'aes-256-cbc' if len(key) == 32 else 'aes-128-cbc',
                       '-e',
                       '-nosalt',
                       '-iv', iv.hex(),
                       '-K', key.hex()],
                       input=(text + pad).encode('ascii'),
                       capture_output=True)
   if r.stderr:
      print(r.stderr.decode('ascii'))
   return iv + r.stdout

def hmac(key, data):
   key = key.hex()
   r = subprocess.run(['openssl', 'mac',
                       '-macopt', 'hexkey:' + key,
                       '-digest', 'sha256',
                       'HMAC'],
                       input=data,
                       capture_output=True)
   return bytes.fromhex(r.stdout.decode('ascii').strip())

def hmac_verify_extract(key, text):
   data, s = text[:-32], text[-32:]
   sig = hmac(key, data)
   if sig != s:
      raise Exception('hmac failed')

   return data

def aes_decrypt_hmac(key, text):
   """Decrypt with AES and validate SHA256 HMAC"""
   return aes_decrypt(key, hmac_verify_extract(key, text))

def aes_encrypt_hmac(key, text):
   """Encrypt with AES and attach a SHA256 HMAC"""
   data = bytes(aes_encrypt(key, text))
   return data + hmac(key, data)

def digest_sha256(text):
   r = subprocess.run(['openssl', 'sha256',
                       '-hex'],
                       input=text,
                       capture_output=True)
   if r.stderr:
      print(r)

   return r.stdout.decode('ascii').split('=')[1].strip()


if __name__ == "__main__":
    parse = argparse.ArgumentParser()

    parse.add_argument('-f', '--file', default='pw.json')
    parse.add_argument('key')

    parse.add_argument('-a', '--add', action='store_true')
    parse.add_argument('name', nargs='?')


    args = parse.parse_args()

    try:
        with open(args.file) as f:
            pw = json.load(f)
        passw = getpass.getpass('Password to access file: ')
    except:
        print('Could not read "%s"; assuming empty file' % args.file)
        pw = None
        for i in range(3):
            passw = getpass.getpass('Password to access file: ')
            passw2 = getpass.getpass('Re-enter: ')
            if passw == passw2:
                # passw2 = hashlib.sha256(passw.encode()).digest()
                passw2 = digest_sha256(passw.encode())
                key = Random.new().read(AES.block_size)
                pw = {'key': base64.b64encode(aes_encrypt_hmac(passw2, key)).decode('ascii')}
                break
            print('Passwords did not match')

        if not pw:
            print('Try again next time')
            sys.exit(0)

    # passw2 = hashlib.sha256(passw.encode()).digest()
    passw2 = digest_sha256(passw.encode())
    passw2 = bytes.fromhex(passw2)
    passw = aes_decrypt_hmac(passw2, base64.b64decode(pw['key']))
    if args.add:
        p = getpass.getpass('Password for %s: ' % args.name)
        pw[args.key] = {'un': args.name,
                        'date': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()),
                        'pw': base64.b64encode(aes_encrypt_hmac(passw, p)).decode('ascii')}
        with open(args.file, "w") as f:
            json.dump(pw, f)

    rec = pw[args.key]
    v = aes_decrypt_hmac(passw, base64.b64decode(rec['pw'])).decode('ascii')
    print('%s\n%s' % (rec['date'], rec['un']))
    sys.stdout.write('%s\r' % v)
    sys.stdout.flush()
    try:
        sys.stdin.read()
    except:
        pass

    print(' ' * (len(v)))

#key = getpass.getpass('Password to access file: ')
#key = digest_sha256(key.encode())
#
## master key
#inp = 'qDh7kkGNjoDKpm0VzAfdQZz6RoATFz3T/t5A1u74TAUIUXem99Tkllsv1fczrC9Lig04l/MsZTZF73ksV/8mO7reIcm4srO+ODC+C8kc+Ic=='
#
#key = bytes.fromhex(key)
#
#inp = base64.b64decode(inp)
#pw = aes_decrypt_hmac(key, inp)
#
## actual entry
#inp = "m+2kzbJG5dxw3gbs+RybFS73HgVe1PfKG512oEqF9ALd1tdSf8+m+63eoJOA9RxQQqhYbxuH7MyVfT2MjWvOrg=="
#inp = base64.b64decode(inp)
#pw = aes_decrypt_hmac(pw, inp)
#print(pw)
