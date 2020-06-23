import argparse
import base64
import getpass
import hashlib
import hmac
import json
import sys
import time
# pip3 install pycrypto
from Crypto import Random
from Crypto.Cipher import AES

def aes_encrypt(key, text):
   """Encrypt text with AES
   16 byte key results in aes-128
   32 byte key results in aes-256
   """
   pad_len = AES.block_size - len(text) % AES.block_size
   pad_char = chr(pad_len)
   pad = pad_len * pad_char
   iv = Random.new().read(AES.block_size)
   enc_state = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(text + pad)
   return enc_state

def aes_decrypt(key, text):
   """Decrypt text with AES"""
   out = AES.new(key, AES.MODE_CBC, text[:AES.block_size]).decrypt(text[AES.block_size:])
   pad_len = out[-1]
   return out[:-pad_len]

def hmac_append(key, text):
   """Append SHA256 HMAC to string"""
   sig = hmac.new(key, text, hashlib.sha256).digest()
   return text + sig

def hmac_verify_extract(key, text):
   """Verify HMAC and extract data"""
   sig_size = hashlib.sha256().digest_size
   sig = text[-sig_size:]
   data = text[:-sig_size]
   # deliberately compare every single character of both digest and sig
   # to eliminate the possibility of a timing attack
   invalid = sum([x != y for x, y in
                         zip(hmac.new(key, data, hashlib.sha256).digest(), sig)])

   if invalid:
      raise Exception('hmac failed')

   return data

def aes_encrypt_hmac(key, text):
   """Encrypt with AES and append SHA256 HMAC"""
   return hmac_append(key, aes_encrypt(key, text))

def aes_decrypt_hmac(key, text):
   """Decrypt with AES and validate SHA256 HMAC"""
   return aes_decrypt(key, hmac_verify_extract(key, text))

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
                passw2 = hashlib.sha256(passw.encode()).digest()
                key = Random.new().read(AES.block_size)
                pw = {'key': base64.b64encode(aes_encrypt_hmac(passw2, key)).decode('ascii')}
                break
            print('Passwords did not match')

        if not pw:
            print('Try again next time')
            sys.exit(0)

    passw2 = hashlib.sha256(passw.encode()).digest()
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
