#!/home/dblume/opt/python-3.9.6/bin/python3
import os
import sys
import time
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import common
import bcrypt
import crypt_utils
import filelock
import config
import getpass


def main(old_user: str, old_pass: str, new_user: str, new_pass: str) -> None:
    start_time = time.time()
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    succeeded = False
    rows = []
    if not new_user:
        new_user = old_user
    if not new_pass:
        new_pass = old_pass
    try:
        old_filename = os.path.join(localdir, 'data', old_user)
        if os.path.exists(old_filename):
            enc_key = bcrypt.hashpw(old_pass.encode(), config.bcrypt_salt)[-32:]
            with filelock.FileLock(old_filename) as lock:
                succeeded, rows = crypt_utils.decrypt_rows(enc_key, old_filename)
        else:
            succeeded = True
            # ID, Type, Description, Username, Password, URL, Custom, Timestamp, Notes
            rows = [['0', 'Web Logins', 'Example Site', 'username', 'correcthorsebatterystaple',
                     'https://example.com', 'custom', str(time.time()), 'Change or delete this entry.']]
            print(f"Creating a new database for {old_user}.")
    except filelock.FileLockException as e:
        print(f"Failed to decrypt rows to new file. Exception: {e}")

    if not succeeded:
        print("Failed to read the old file. Bad passphrase or username?")
        return

    new_filename = os.path.join(localdir, 'data', new_user)
    if os.path.exists(new_filename + ".enc"):
        common.backup_files(filename)
        print("Backed up a previous copy of the new username's files.")

    enc_key = bcrypt.hashpw(new_pass.encode(), config.bcrypt_salt)[-32:]
    succeeded = False
    try:
        new_filename = os.path.join(localdir, 'data', new_user)
        with filelock.FileLock(new_filename) as lock:
            crypt_utils.encrypt_rows(enc_key, rows, new_filename)
            succeeded = True
    except filelock.FileLockException as e:
        print(f"Failed to encrypt to new username. Exception: {e}")

    if succeeded:
        print(f"Done. That took {(time.time() - start_time):1.2f}s.")
    else:
        print("Failed.")


if __name__ == '__main__':
    desc = """Create a new account, or change username or password.

Example:

New account:
------------

To create a new account, myusername, run:

    ./%(prog)s myusername

Changing a username and password:
---------------------------------

To convert the existing database "olduser" to "aaron", you have to pass "olduser"
as an argument, and specify two options.

    ./%(prog)s -u aaron -p xvdfkj23_ olduser
"""

    parser = ArgumentParser(description=desc,
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-u", "--new_user")
    parser.add_argument("-p", "--new_pass")
    parser.add_argument("old_user")
    parser.set_defaults(new_user="", new_pass="")
    args = parser.parse_args()
    old_pass = getpass.getpass(f'Password for {args.old_user}:')
    main(args.old_user, old_pass, args.new_user, args.new_pass)
