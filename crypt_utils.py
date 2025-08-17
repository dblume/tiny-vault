#!/usr/bin/env python3
# http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
import string
import os
import sys
import gzip
import io  # Use this for in-memory files.
from Crypto.Cipher import AES
import bcrypt
import hashlib
import secrets
import struct
import csv
import time
import base64
import config
from typing import BinaryIO, Sequence


class crypt_util_error(Exception):
    pass


def encrypt_file(key: bytes, in_file: BinaryIO, out_filename: str, chunksize: int=64 * 1024) -> None:
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_file:
            Input file-type object

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    iv = secrets.token_bytes(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
#    filesize = os.path.getsize( in_filename )

    # This works for files and cString() objects
    in_file.seek(0, os.SEEK_END)
    filesize = in_file.tell()
    in_file.seek(0, os.SEEK_SET)

    with open(out_filename, 'wb') as outfile:
        outfile.write(struct.pack('<Q', filesize))
        outfile.write(iv)
        while True:
            chunk = in_file.read(chunksize)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk += (' ' * (16 - len(chunk) % 16)).encode('utf-8')
            outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key: bytes, in_filename: str, out_file: BinaryIO, chunksize: int=24 * 1024) -> bool:
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file.
    """
    if not os.path.exists(in_filename):
        return False
    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        while True:
            chunk = infile.read(chunksize)
            if len(chunk) == 0:
                break
            out_file.write(decryptor.decrypt(chunk))
        out_file.truncate(origsize)
    return True


def read_csv(filename: str) -> Sequence[Sequence[str]]:
    rows = []
    with open(filename, 'rb') as f:
        rows = convert_csv_rows(f)
    return rows


def convert_csv_rows(f: BinaryIO) -> Sequence[Sequence[str]]:
    rows = []
    reader = csv.reader(f)
    # Read in:
    # Type, Description, Username, Password, URL, Custom, Updated, Notes
    #
    # Transform to:
    # ID, Type, Description, Username, Password, URL, Custom, Timestamp, Notes
    row_num = 0
    for row in reader:
        row_num += 1
        if row_num == 1:
            continue
        if len(row) != 8:
            raise crypt_util_error("Row %d had %d fields instead of 8." % (row_num, len(row)))
        stamp = time.mktime(time.strptime(row[6], '%d-%b-%y'))
        row.insert(0, row_num - 1)
        row[7] = stamp
        rows.append(row)
    return rows


def encrypt_rows(enc_key: bytes, rows: Sequence[Sequence[str]], out_filename: str) -> None:
    sio = io.StringIO()
    writer = csv.writer(sio)
    writer.writerows(rows)
    bytes_ = sio.getvalue().encode('utf-8')
    sio.close()
    bio = io.BytesIO(bytes_)  # TODO see if there a more direct way from rows to bytes.
    md5_hash = hashlib.md5(bytes_).hexdigest()
    with open(out_filename + '.hash', 'wb') as h:
        h.write(md5_hash.encode())
    encrypt_file(enc_key, bio, out_filename + '.enc', 16 * 1024)
    bio.close()


def decrypt_rows(enc_key: bytes, in_filename: str) -> tuple[bool, Sequence[Sequence[str]]]:
    """ returns True, rows upon success """
    rows = []
    bio = io.BytesIO()
    if not decrypt_file(enc_key, in_filename + '.enc', bio, 16 * 1024):
        return False, rows
    bio.seek(0)
    with open(in_filename + '.hash', 'rb') as h:
        file_hash = h.read()
    if file_hash != hashlib.md5(bio.getvalue()).hexdigest().encode():
        return False, rows
    sio = io.StringIO(bio.getvalue().decode('utf-8'))
    bio.close()
    reader = csv.reader(sio)
    for row in reader:
        rows.append(row)
    sio.close()
    return True, rows


if __name__ == '__main__':
    import filelock
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    username = 'test'
    print("Start!")

    rows = read_csv(os.path.join(localdir, 'splash_id_archive_CC_ID_fewer_columns.csv'))

    enc_key = bcrypt.hashpw(b"passw0rd", config.bcrypt_salt)[-32:]
    encrypt_rows(enc_key, rows, os.path.join(localdir, 'data', username))

    with filelock.FileLock(os.path.join(localdir, 'data', username)) as lock:
        succeeded, out_rows = decrypt_rows(enc_key, os.path.join(localdir, 'data', username))
    print("decrypt_rows succeeded =", succeeded)

#    my_hash = hashlib.sha224("Nobody inspects the spammish repetition").hexdigest()
#    print my_hash


#    hashed = bcrypt.hashpw( "password", config.bcrypt_salt )[-32:]


#    session = base64.b64decode(urllib.unquote(cookie_val))
#    urllib.quote_plus(string[, safe]) ?

#    print "bcrypt hashed", hashed

#
# bcrypt
#
#    hashed = bcrypt.hashpw("password", bcrypt.gensalt())
#    # gensalt's log_rounds parameter determines the complexity.
#    # The work factor is 2**log_rounds, and the default is 12
#    hashed = bcrypt.hashpw("password", bcrypt.gensalt(10))
#    print hashed


#    encrypt_file(key, os.path.join( localdir, "source_file_for_encryption.txt"))
#    decrypt_file(key, \
#                  os.path.join(localdir, "source_file_for_encryption.txt.enc"), \
#                  os.path.join(localdir, "decrypted_file.txt"))

    print("Done.")
