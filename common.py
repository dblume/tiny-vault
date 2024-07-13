#!/home/dblume/opt/python-3.9.6/bin/python3
#
# common.py by David Blume


import os
import sys
import cgi
import bcrypt
import crypt_utils
import filelock
import shutil
from itertools import cycle
import base64

def xor_crypt_string(data, key):
    #with open('dxb.txt', 'w') as f:
    #    f.write(f'DXB {type(data)=} {data=} {type(key)=} {key=}')
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in zip(data, cycle(key)))


def salt_cookie_data(data, salt):
    # print(f'DXB {data=}')
    return base64.b64encode(xor_crypt_string(data.decode(), salt).encode()).decode()


def restore_from_salted_cookie(cookie, salt):
    return xor_crypt_string(base64.b64decode(cookie).decode(), salt)


def verify_user(localdir, username, password, session=""):
    message = ""
    bcrypt_salt = '$2a$12$0S7xZwmn6w4xmuY1x5X26O' # Made by bcrypt.gensalt()
    if len(session):
        enc_key = session
    else:
        enc_key = bcrypt.hashpw(password.encode(), bcrypt_salt.encode())[-32:]
    filename = os.path.join(localdir, 'data', username)
    try:
        with filelock.FileLock(filename) as lock:
            succeeded, rows = crypt_utils.decrypt_rows(enc_key, filename)
#            if succeeded == False:
#                message = 'Unexpected: decrypt_rows failed. ' # + enc_key
    except filelock.FileLockException as e:
        succeeded = False
        rows = []
        message = "filelock timed out."
    return succeeded, enc_key, rows, message


def backup_files(filename):
    prev_enc = filename + ".enc_prev"
    prev_hash = filename + ".hash_prev"
    if os.path.exists(prev_enc):
        os.unlink(prev_enc)
    shutil.copyfile(filename + ".enc", prev_enc)
    if os.path.exists(prev_hash):
        os.unlink(prev_hash)
    shutil.copyfile(filename + ".hash", prev_hash)


def form_quote(t):
    """HTML-escape for form input the text in `t`."""
    return (t.replace('"', "&quot;"))


checkmark_char = '<span style="color: green; font-size: 20px">&#10003;</span>'

error_char = '<span style="color: red; font-size: 32px">&#9888;</span>'


if __name__=='__main__':
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))

    print("Done.")


