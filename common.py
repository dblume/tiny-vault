#!/usr/bin/env python3
import os
import sys
import cgi
import bcrypt
import crypt_utils
import filelock
import shutil
from itertools import cycle
import base64
import config
from typing import Sequence


def xor_crypt_string(data: str, key: str) -> str:
    return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, cycle(key)))


def salt() -> str:
    # Used only for cookies.
    return config.cookie_salt + os.environ['REMOTE_ADDR']


def salt_cookie_data(data: str, salt: str) -> str:
    return base64.b64encode(xor_crypt_string(data.decode(), salt).encode()).decode()


def restore_from_salted_cookie(cookie: str, salt: str) -> str:
    return xor_crypt_string(base64.b64decode(cookie).decode(), salt)


def verify_user(localdir: str, username: str, password: str, session: str=""
        ) -> tuple[bool, str, Sequence[Sequence[str]], str]:
    message = ""
    if len(session):
        enc_key = session
    else:
        enc_key = bcrypt.hashpw(password.encode(),
                                config.bcrypt_salt)[-32:]
    filename = os.path.join(localdir, 'data', username)
    try:
        with filelock.FileLock(filename) as lock:
            succeeded, rows = crypt_utils.decrypt_rows(enc_key, filename)
    except filelock.FileLockException as e:
        succeeded = False
        rows = []
        message = "filelock timed out."
    except UnicodeDecodeError as e:
        succeeded = False
        rows = []
        message = ""  # This message gets displayed, don't want to say anything yet.
    return succeeded, enc_key, rows, message


def backup_files(filename: str) -> None:
    prev_enc = filename + ".enc_prev"
    prev_hash = filename + ".hash_prev"
    if os.path.exists(prev_enc):
        os.unlink(prev_enc)
    shutil.copyfile(filename + ".enc", prev_enc)
    if os.path.exists(prev_hash):
        os.unlink(prev_hash)
    shutil.copyfile(filename + ".hash", prev_hash)


def form_quote(t: str) -> str:
    """HTML-escape for form input the text in `t`."""
    return (t.replace('"', "&quot;"))


checkmark_char = '<span style="color: green; font-size: 20px">&#10003;</span>'

error_char = '<span style="color: red; font-size: 32px">&#9888;</span>'


if __name__ == '__main__':
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))

    print("Done.")
