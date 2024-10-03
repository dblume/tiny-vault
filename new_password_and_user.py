#!/home/dblume/opt/python-3.9.6/bin/python3
#
# Example:
#
# Ensure you have "export HISTCONTROL=ignorespace" in your .bash_profile,
# so that you can have your history ignore commands that start with a space.
#
# Then,
#
# To convert the existing database "test" to "aaron", you have to pass "test"
# as an argument, and specify three options.
#
#  ./new_password_and_user.py --new_user=aaron --old_pass=passw0rd --new_pass=sdfkj23_ test
#
# ^ See that extra space at the beginning?  That's so the command won't go in the history.
import os
import sys
import time
from argparse import ArgumentParser
import common
import bcrypt
import crypt_utils
import filelock
import config


def main(old_user: str, old_pass: str, new_user: str, new_pass: str):
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
            rows = [['0', 'web', 'Example Site', 'username', 'correcthorsebatterystaple',
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
    parser = ArgumentParser(description='Assign a new pasword or user.')
    parser.add_argument("-u", "--new_user")
    parser.add_argument("-n", "--new_pass")
    parser.add_argument("old_user")
    parser.add_argument("old_pass")
    parser.set_defaults(new_user="", old_pass="")
    args = parser.parse_args()
    main(args.old_user, args.old_pass, args.new_user, args.new_pass)
