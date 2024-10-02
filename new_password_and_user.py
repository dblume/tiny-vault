#!/home/dblume/opt/python-3.9.6/bin/python3
# chmod 755 me, and make sure I have UNIX style newlines.
# "-u" is for unbuffered binary output
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
from optparse import OptionParser
import common
import bcrypt
import crypt_utils
import filelock
import config


def main(old_user, old_pass, new_user, new_pass, debug):
    start_time = time.time()
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    succeeded = False
    enc_key = bcrypt.hashpw(old_pass.encode(), config.bcrypt_salt)[-32:]
    rows = []
    try:
        old_filename = os.path.join(localdir, 'data', old_user)
        with filelock.FileLock(old_filename) as lock:
            succeeded, rows = crypt_utils.decrypt_rows(enc_key, old_filename)
    except filelock.FileLockException as e:
        print("Failed to decrypt rows to new file. Exception:", e)

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
        print("Failed to encrypt to new username. Exception:", e)

    if succeeded:
        print("Done. That took %1.2fs." % (time.time() - start_time))
    else:
        print("Failed.")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug")
    parser.add_option("-u", "--new_user", type="string", dest="new_user")
    parser.add_option("-o", "--old_pass", type="string", dest="old_pass")
    parser.add_option("-n", "--new_pass", type="string", dest="new_pass")
    parser.set_defaults(debug=False,
                        new_user="new_user",
                        old_pass="passw0rd",
                        new_pass="passw0rd")
    options, args = parser.parse_args()
    print("args", args)
    print("options", options)
    if len(args) != 1:
        print("Error: You have to specify an existing database.")
        sys.exit(0)
    main(args[0], options.old_pass, options.new_user, options.new_pass, options.debug)
