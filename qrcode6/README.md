QR Code generator
=================

Google Authenticator needs a QR Code to get the secret for timed one-time
passcodes. The QR Codes reasonably fitting such purpose are Version 6 through 9.

QR Code is just a bit stream with error correction attached, so the reader can
read it back even if the code is damaged, or cannot be discerned accurately due
to lighting.

The level of error correction is variable. However, for the purpose of reading
QR Code off the screen, Low level is sufficient.

The type of content can be selected to conserve space (eg alphanumeric).
However, for the purpose of Google Authenticator the content of type Byte is
good enough - there really is no space constraint, and the use of case-sensitive
strings is useful for human readability.

The Mask pattern for the payload is also variable, but for the purpose of
producing QR Code for Google Authenticator one fixed pattern seems to work just
fine - the sort of strings encoded do not have inherent bit patterns that would
affect readability of the QR Code.

Producing QR Code
-----------------
To produce QR Code for Google Authenticator, construct a string like:

`otpauth://totp/Menlo%20Security:mock.user@menlosecurity.com?secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=Menlo%20Security&algorithm=SHA1&digits=6&period=30`

Here the user id can be anything, the secret is base-32-encoded secret (not
base-64), the issuer is a string that helps identify the key among multiple keys
stored in Google Authenticator. The algorithm, digits, and period are ignored by
Google Authenticator (they are assumed to be `SHA1`, `6`, and `30`
respectively), and can be omitted, but other authenticators may use them.

Such a string should be shorter than 230 bytes (which normally it will be). Pass
the string to `qr_code` generator function. It will yield the size of the square
followed by tuples of x and y coordinates setting the black dots. You need to
consume these to produce an image.

An example in `gen.py` consumes the matrix to print a QR Code using unicode 
characters on the terminal. Some terminals may have line spacing that makes it
look like a broken pattern. Adjust the spacing for the pattern to look joined
(and square).

Producing PNG
-------------
A simple grayscale PNG can be constructed for a given string.
`qr_png(s, scale=4)` returns a byte string and a width of the image in pixels.

This can be embedded in HTML as a data: URL, like `png.py` does.
