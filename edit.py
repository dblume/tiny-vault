#!/home/dblume/opt/python-3.9.6/bin/python3
#
# edit.py by David Blume

import os
import sys
import codecs
import time
import http.cookies
import cgi
import cgitb
import html
import constants
import string
import common
import crypt_utils
import filelock
import transactionlog
import gen_password

cgitb.enable(display=0, logdir="tmp")


def print_edit_form(row):
    # ID, Type, Description, Username, Password, URL, Custom, Timestamp, Notes
    # (type) desc user sess url custom notes
    suggested_password = " (or change it to " + gen_password.password() + ")"
    if int(row[0]) == -1:
        delete_button = ''
        last_edited = ''
    else:
        delete_button = ' &nbsp;<input type="submit" name="submit" onclick="document.pressed=this.value" value="Delete">'
        last_edited = '<br /><span style="color:grey">Last edited on %s.</span>' % (time.strftime("%Y-%m-%d", time.localtime(float(row[7]))),)
    defaults = (row[2], row[3], common.form_quote(row[4]), suggested_password, row[5], row[6], row[8], last_edited, delete_button)
    print(constants.edit_form_text_start)
    print('<select name="type">')
    for key in sorted(constants.type_map.keys()):
        selected = ""
        if row[1] == key:
            selected = " selected"
        print('    <option%s value="%s">%s</option>' % (selected, constants.type_map[key], key))
    print('</select><input type="hidden" name="id" value="%s">' % row[0])
    print(constants.edit_form_text_end % defaults)


def get_cookie(my_cookie):
    have_cookie = False
    username = ''
    session = ''
    verified_session = False
    rows = []
    if 'HTTP_COOKIE' in os.environ:
        my_cookie.load(os.environ['HTTP_COOKIE'])
        if 'user' in my_cookie:
            have_cookie = True
            username = my_cookie['user'].value
            my_cookie['user']['domain'] = '.' + localdir_basename
            if 'sess' in my_cookie:
                my_cookie['sess']['domain'] = '.' + localdir_basename
                if len(my_cookie['sess'].value) > 0:
                    session = common.restore_from_salted_cookie(my_cookie['sess'].value, common.salt())
                    verified_session, enc_key, rows, verify_msg = common.verify_user(localdir, username, "", session)
                else:
                    verify_msg = "The session cookie is empty. <strong>macOS: Try relaunching Safari. (Really.)</strong><br />"
                    verify_msg += str(os.environ['HTTP_COOKIE'])
                    verify_msg += "<br />\n"
                    if isinstance(os.environ['HTTP_COOKIE'], str):
                        verify_msg += "Yes it is a str"
            else:
                verify_msg = "No sess cookie. <strong>iOS: Try relaunching Safari.</strong><br />"
        else:
            verify_msg = "No user cookie<br />"
    else:
        verify_msg = "No HTTP_COOKIE at all.<br />"
    return have_cookie, verified_session, username, session, rows, verify_msg


def get_row_index(rows, id):
    found_row = False
    for i, row in enumerate(rows):
        if int(id) == int(row[0]):
            found_row = True
            break
    return found_row, i


def delete_row(localdir, username, session, rows, id):
    succeeded = False

    found_row, index = get_row_index(rows, id)
    if not found_row:
        return False

    rows.pop(index)

    try:
        filename = os.path.join(localdir, 'data', username)
        with filelock.FileLock(filename) as lock:
            # Backup
            common.backup_files(filename)
            crypt_utils.encrypt_rows(session, rows, filename)
            succeeded = True
    except filelock.FileLockException as e:
        succeeded = False
    return succeeded


def change_row(localdir, username, session, rows, row):
    succeeded = False

    found_row, index = get_row_index(rows, row[0])
    if not found_row:
        rows.append(row)
    else:
        rows[index] = row

    try:
        filename = os.path.join(localdir, 'data', username)
        with filelock.FileLock(filename) as lock:
            common.backup_files(filename)
            crypt_utils.encrypt_rows(session, rows, filename)
            succeeded = True
    except filelock.FileLockException as e:
        succeeded = False
    return succeeded


def get_new_id(rows):
    last_max = 0
    for r in rows:
        if int(r[0]) > last_max:
            last_max = int(r[0])
    return str(last_max + 1)


if __name__ == '__main__':
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    localdir_basename = os.path.basename(localdir)

    form_data = cgi.FieldStorage()
    my_cookie = http.cookies.SimpleCookie()
    verified_session = False
    username = ''
    session = ''
    special_message = ''
    transaction_message = ''
    verify_msg = ''
    have_cookie = False
    row = [-1, "Web Logins", "", "", gen_password.password(), "https://", "", 0, ""]
    target = "new"
    should_print_edit_form = True
    tlog = transactionlog.Transaction_log(os.path.join(localdir, 'log.txt'))

    if 'submit' in form_data:
        submit = form_data['submit'].value
        id = form_data['id'].value
        if submit == 'Delete':
            should_print_edit_form = False
            have_cookie, verified_session, username, session, rows, verify_msg = get_cookie(my_cookie)
            if verified_session:
                succeeded = delete_row(localdir, username, session, rows, id)
                if succeeded:
                    transaction_message = common.checkmark_char + ' The row was deleted. You can <a href="index.py">go back</a>.<br />'
                    tlog.log(os.environ['REMOTE_ADDR'], 'delete', '')
                else:
                    transaction_message = common.error_char + ' The row couldn\'t be deleted. You can <a href="index.py">try again</a>.<br />'
                    tlog.log(os.environ['REMOTE_ADDR'], 'delete', 'attempt failed')
            else:
                transaction_message = common.error_char + ' Could not verify your session to delete the row. <a href="index.py?do=logout">Login again</a>, please.<br />'
                tlog.log(os.environ['REMOTE_ADDR'], 'delete', 'authentication failed')
        elif submit == 'OK':
            should_print_edit_form = False
            desc = ''
            user = ''
            sess = ''
            url = ''
            custom = ''
            notes = ''
            rev_type_map = dict((v, k) for k, v in constants.type_map.items())
            type = rev_type_map[form_data['type'].value]
            if 'desc' in form_data:
                desc = html.escape(form_data['desc'].value)
            if 'user' in form_data:
                user = html.escape(form_data['user'].value)
            if 'sess' in form_data:
                sess = html.escape(form_data['sess'].value)
            if 'url' in form_data:
                url = form_data['url'].value
            if 'custom' in form_data:
                custom = html.escape(form_data['custom'].value)
            if 'notes' in form_data:
                notes = html.escape(form_data['notes'].value)
            have_cookie, verified_session, username, session, rows, verify_msg = get_cookie(my_cookie)
            row_change_text = 'changed'
            if int(id) == -1:
                row_change_text = 'added'
            if verified_session:
                if int(id) == -1:
                    id = get_new_id(rows)
                row = [id, type, desc, user, sess, url, custom, str(time.time()), notes]
                succeeded = change_row(localdir, username, session, rows, row)
                if succeeded:
                    transaction_message = '%s The row was %s. You can <a href="index.py">go back to see it in the list</a>.<br />' % (common.checkmark_char, row_change_text,)
                    tlog.log(os.environ['REMOTE_ADDR'], row_change_text, '')
                else:
                    transaction_message = '%s The row couldn\'t be %s. You can <a href="index.py">try again</a>.<br />' % (common.error_char, row_change_text)
                    tlog.log(os.environ['REMOTE_ADDR'], row_change_text, 'attempt failed')
            else:
                transaction_message = '<p><span style="color: red; font-weight: bold;">%s Could not verify your session. The row was not %s.</span> <em><strong>Copy your changes</strong> from below</em> and <a href="index.py?do=logout">login again</a> to try again, please.</p>' % (common.error_char, row_change_text)
                transaction_message += '<strong>Description</strong>: %s<br /><strong>Name</strong>: %s<br /><strong>Password</strong>: %s<br /><strong>URL</strong>: %s<br /><strong>Custom</strong>: %s<br /><strong>Notes</strong>: %s<br />' % (desc, user, sess, url, custom, notes)
                tlog.log(os.environ['REMOTE_ADDR'], 'change', 'authentication failed')
        elif submit == 'Cancel':
            should_print_edit_form = False
            transaction_message = 'No change made. You can <a href="index.py">go back to the list</a>.<br />'
            tlog.log(os.environ['REMOTE_ADDR'], 'cancel', '')
    else:
        if "id" in form_data:
            target = form_data["id"].value
        have_cookie, verified_session, username, session, rows, verify_msg = get_cookie(my_cookie)
        if verified_session:
            if target != "new":
                target_id = int(target)
                for r in rows:
                    if int(r[0]) == target_id:
                        row = r
                        break
        else:
            transaction_message = common.error_char + ' Could not verify your session. <a href="index.py?do=logout">Login again</a>, please.<br />'
            transaction_message += verify_msg  # delete this line
            tlog.log(os.environ['REMOTE_ADDR'], 'edit', 'verification failed')
            should_print_edit_form = False

#    if have_cookie:
#        print my_cookie
    print("Content-type: text/html; charset=utf-8\n\n")

    print(constants.html_head_text % (os.environ['SERVER_NAME'], os.environ['SERVER_NAME']))
    if should_print_edit_form:
        print('  <meta name="viewport" content="width=400, initial-scale=1.0"/> <!-- maximum-scale=1.0; user-scalable=0;"/>  -->')
        print(constants.edit_form_validator_text)
        default_focus_text = ' OnLoad="document.editform.desc.focus();"'
    else:
        default_focus_text = ''

    print(constants.close_head_text % (default_focus_text,))

    #
    # Begin body
    #
    print(constants.html_body_prefix_text)

    if len(special_message):
        print(special_message)

    # print '<a href="/index.py">Back to the list</a>.<div style="text-align:right">%s <a href="index.py?do=logout">logout</a></div><br />' % username
    print('<div><span><a href="/index.py">Back to the list</a>.</span><div style="float: right; text-align:right">%s <a href="index.py?do=logout">logout</a></div></div><br />' % username)

    if len(transaction_message):
        print(transaction_message)

#    for k in sorted(form_data.keys()):
#        print "%s: %s<br />" % (k, form_data[k])

    if should_print_edit_form:
        print('<div style="position:absolute; top:30%; margin-top: -90px; left:50%; margin-left: -188px">')
        print_edit_form(row)
        print('</div>')

    print(constants.html_footer_text)
