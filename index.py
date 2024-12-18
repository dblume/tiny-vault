#!/usr/bin/env python3
import os
import sys
import codecs
import time
import http.cookies
import cgi
import cgitb
import constants
import string
from pathlib import Path
import common
import transactionlog
import logging

__author__ = 'David Blume'
__copyright__ = "Copyright 2011, David Blume"
__license__ = "Apache 2.0"
__version__ = "1.0"

cgitb.enable(display=0, logdir="tmp")


def print_login_form(username: str) -> None:
    print(constants.login_form_text % username)


def user_text_is_valid(s: str) -> bool:
    allowed_letters = string.ascii_letters + string.digits + '_'
    for c in s:
        if c not in allowed_letters:
            return False
    return True


if __name__ == '__main__':
    logging.basicConfig(filename='index.py.log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        # datefmt='%Y-%m-%d %H:%M',
                        level=logging.INFO)
    logger = logging.getLogger('index')
    logger.debug('Starting')
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    localdir_basename = os.path.basename(localdir)

    form_data = cgi.FieldStorage()
    my_cookie = http.cookies.SimpleCookie()
    username = ''
    session = ''
    special_message = ''
    verify_msg = ''
    have_cookie = False

    should_print_failed_login = False
    logger.debug('Before transaction log')
    tlog = transactionlog.Transaction_log(os.path.join(localdir, 'log.txt'), logger)
    logger.debug('Have transaction log')

    if "user" in form_data and "pass" in form_data:
        logger.debug('Have user and pass')
        should_print_login_form = False
        username = form_data["user"].value.strip()
        passphrase = form_data["pass"].value

        if not user_text_is_valid(username):
            verified = False
        else:
            verified, enc_key, rows, verify_msg = common.verify_user(localdir, username, passphrase)
        if not verified:
            should_print_failed_login = True
            should_print_login_form = True
            tlog.log(os.environ['REMOTE_ADDR'], 'login', username[:2] + "\u2026" + ' failed')
            time.sleep(2)
        else:
            # Sending a cookie.
            my_cookie['user'] = username
            my_cookie['user']['max-age'] = 14 * 24 * 60 * 60
            my_cookie['user']['domain'] = '.' + localdir_basename
            my_cookie['user']['secure'] = 'on'
            my_cookie['user']['httponly'] = 'on'
            my_cookie['sess'] = common.salt_cookie_data(enc_key, common.salt())
            my_cookie['sess']['max-age'] = 30 * 60
            my_cookie['sess']['domain'] = '.' + localdir_basename
            my_cookie['sess']['secure'] = 'on'
            my_cookie['sess']['httponly'] = 'on'
            have_cookie = True
            tlog.log(os.environ['REMOTE_ADDR'], 'login', username[:2] + "\u2026")
            # touch a file at time of sign-in
            Path('data', username + '.sessiontime').touch()
    else:
        should_print_login_form = True
        reset_cookie = False

        if "do" in form_data:
            action = form_data["do"].value
            if action == "logout":
                reset_cookie = True
                tlog.log(os.environ['REMOTE_ADDR'], 'logout', '')

        if 'HTTP_COOKIE' in os.environ:
            my_cookie.load(os.environ['HTTP_COOKIE'])
            if 'user' in my_cookie:
                # have_cookie = True  # No need to re-send cookie.
                username = my_cookie['user'].value
                my_cookie['user']['domain'] = '.' + localdir_basename
                if reset_cookie:
                    my_cookie['sess'] = ""
                    my_cookie['sess']['max-age'] = 1
                    my_cookie['sess']['domain'] = '.' + localdir_basename
                    have_cookie = True
                    # my_cookie['sess']['expires'] = 'Wed, 21 Oct 2015 07:28:00 GMT'
                elif 'sess' in my_cookie:
                    session = common.restore_from_salted_cookie(my_cookie['sess'].value, common.salt())
                    my_cookie['sess']['domain'] = '.' + localdir_basename
                    verified, enc_key, rows, verify_msg = common.verify_user(localdir, username, "", session)
                    if verified:
                        sess_path = Path('data', username + '.sessiontime')
                        if sess_path.exists() and sess_path.stat().st_mtime > time.time() - 60 * 30:
                            tlog.log(os.environ['REMOTE_ADDR'], 'view', '')
                            should_print_login_form = False
                        else:
                            tlog.log(os.environ['REMOTE_ADDR'], 'view', username[:2] + "\u2026" + ' session rejection')
                            special_message = 'Session missing or expired.'
                    else:
                        tlog.log(os.environ['REMOTE_ADDR'], 'view', username[:2] + "\u2026" + ' returning cookie authentication failed')

    if have_cookie:
        logger.debug('Have cookie')
        print(my_cookie)
    print("Content-type: text/html; charset=utf-8\n\n")

    print(constants.html_head_text % (os.environ['SERVER_NAME'], os.environ['SERVER_NAME']))
    too_many_login_attempts = not tlog.allow(os.environ['REMOTE_ADDR'], 'login')
    if should_print_login_form:
        if not too_many_login_attempts:
            logger.debug('Printing login form')
            print('  <meta name="viewport" content="width=device-width, initial-scale=1.0 maximum-scale=2.0, user-scalable=1">')
            print(constants.login_form_validator_text)
            if len(username):
                default_focus_text = ' OnLoad="document.loginform.pass.focus();"'
            else:
                default_focus_text = ' OnLoad="document.loginform.user.focus();"'
        else:
            default_focus_text = ''
            print('<strong>Too many failed login attempts.</strong>')
    else:
        print('  <meta name="viewport" content="width=500, initial-scale=1.0"> <!-- maximum-scale=1.0, user-scalable=0,"/>  -->')
        print(constants.html_head_table_style)
        default_focus_text = ' OnLoad="document.filterform.filter.focus();"'

    print(constants.close_head_text % (default_focus_text,))

    #
    # Begin body
    #
    if should_print_login_form:
        # If the "fork me" image exists, then use it. No worries if not.
        if os.path.isfile('images/forkme_right_orange_ff7600.png'):
            print('<a href="https://github.com/dblume/tiny-vault"><img decoding="async" '
                  'width="149" height="149" style="position: absolute; opacity: 0.5; top: 0; right: 0; border: 0;" '
                  'src="images/forkme_right_orange_ff7600.png" class="attachment-full size-full" '
                  'alt="Fork me on GitHub" loading="lazy"></a>')
    else:
        print(constants.table_sorter_headers_text)
    print(constants.html_body_prefix_text)

    if len(special_message):
        print(special_message)

    if should_print_login_form:
        if not too_many_login_attempts:
            print('<div style="position:absolute; top:25%; margin-top: -48px; left:50%; margin-left: -203px">')
            if should_print_failed_login:
                print("<p><b>Sorry! That username or passphrase is incorrect.</b></p>")
                if len(verify_msg):
                    print(f"<p>{verify_msg}</p>")
            print_login_form(username)
            print('</div>')
        print(constants.credits_text)
    else:
        print(f'<div style="text-align:right">{username} <a href="index.py?do=logout">logout</a></div><br>')
#        print '<div class="note"><strong>TIP:</strong> Sort multiple columns by holding down the <strong>shift</strong> key when clicking another header.</div><br>'
        print(constants.table_header)
        for id, type, desc, user, pwd, url, cust, ts, notes in rows:
            print("<tr>")
            print(f"    <td><a href=\"edit.py?id={id}\">Edit</a></td>")
            print(f"    <td>{type}</td>")
            if url.startswith('http'):
                print(f"    <td><a href=\"{url}\">{desc}</a></td>")
            else:
                print(f"    <td>{desc}</td>")
            date = f'<span style="color:lightgrey">{time.strftime("%Y-%m-%d", time.localtime(float(ts)))}</span>'
            print("    <td>%s</td>\n    <td class=\"m\">%s</td>\n    <td>%s</td>\n    <td>%s %s</td>" % (user, pwd, cust, notes, date))
            print("</tr>")
        print(constants.table_footer)

    print(constants.html_footer_text)
    logging.debug('Done. Printed footer.')
