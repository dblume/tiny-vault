#!/usr/bin/python
#!C:/Python26/python.exe
# Also restore my_cookie['user']['domain']
# index.py by David Blume

import os
import sys
import codecs
import time
import Cookie
import cgi, cgitb
import constants
import string
import common
import transactionlog
import logging

cgitb.enable(display=0, logdir="/home/dblume/secure.dlma.com/tmp")

def print_login_form(username):
    print constants.login_form_text % username


def user_text_is_valid(s):
    allowed_letters = string.letters + string.digits + '_'
    for c in s:
        if c not in allowed_letters:
            return False
    return True


if __name__=='__main__':
    logging.basicConfig(filename='index.py.log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        #datefmt='%Y-%m-%d %H:%M',
                        level=logging.INFO)
    logger = logging.getLogger('index')
    logger.debug('Starting')
    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))

    form_data = cgi.FieldStorage()
    my_cookie = Cookie.SimpleCookie()
    username = ''
    session = ''
    special_message = ''
    verify_msg = ''
    have_cookie = False

    should_print_failed_login = False;
    logger.debug('Before transaction log')
    tlog = transactionlog.Transaction_log(os.path.join(localdir, 'log.txt'), logger)
    logger.debug('Have transaction log')

    if "user" in form_data and "pass" in form_data:
        logger.debug('Have user and pass')
        should_print_login_form = False
        username = form_data["user"].value.strip()
        password = form_data["pass"].value

        if not user_text_is_valid(username):
            verified = False
        else:
            verified, enc_key, rows, verify_msg = common.verify_user(localdir, username, password)
        if not verified:
            should_print_failed_login = True
            should_print_login_form = True
            tlog.log(os.environ['REMOTE_ADDR'], 'login', username[:2] + u"\u2026" + ' failed')
            time.sleep( 2 )
        else:
            # Sending a cookie.
            my_cookie['user'] = username
            my_cookie['user']['max-age'] = 14*24*60*60
            my_cookie['user']['domain'] = '.secure.dlma.com'
            my_cookie['user']['secure'] = 'on'
            my_cookie['user']['httponly'] = 'on'
            my_cookie['sess'] = common.salt_cookie_data(enc_key, os.environ['REMOTE_ADDR'])
            my_cookie['sess']['max-age'] = 30*60
            my_cookie['sess']['domain'] = '.secure.dlma.com'
            my_cookie['sess']['secure'] = 'on'
            my_cookie['sess']['httponly'] = 'on'
            have_cookie = True
            tlog.log(os.environ['REMOTE_ADDR'], 'login', username[:2] + u"\u2026")
    else:
        should_print_login_form = True
        reset_cookie = False

        if "do" in form_data:
            action = form_data["do"].value
            if action == "logout":
                reset_cookie = True
                tlog.log(os.environ['REMOTE_ADDR'], 'logout', '')

        if os.environ.has_key('HTTP_COOKIE'):
            my_cookie.load(os.environ['HTTP_COOKIE'])
            if my_cookie.has_key('user'):
                # have_cookie = True  # No need to re-send cookie.
                username = my_cookie['user'].value
                my_cookie['user']['domain'] = '.secure.dlma.com'
                if reset_cookie:
                    my_cookie['sess'] = ""
                    my_cookie['sess']['max-age'] = 1
                    my_cookie['sess']['domain'] = '.secure.dlma.com'
                    have_cookie = True
                    # my_cookie['sess']['expires'] = 'Wed, 21 Oct 2015 07:28:00 GMT'
                elif my_cookie.has_key('sess'):
                    session = common.restore_from_salted_cookie(my_cookie['sess'].value, os.environ['REMOTE_ADDR'])
                    my_cookie['sess']['domain'] = '.secure.dlma.com'
                    verified, enc_key, rows, verify_msg = common.verify_user(localdir, username, "", session)
                    if verified:
                        tlog.log(os.environ['REMOTE_ADDR'], 'view', '')
                        should_print_login_form = False
                    else:
                        tlog.log(os.environ['REMOTE_ADDR'], 'view', username[:2] + u"\u2026" + ' returning cookie authentication failed')

    if have_cookie:
        logger.debug('Have cookie')
        print my_cookie
    print "Content-type: text/html; charset=utf-8\n\n"

    print constants.html_head_text
    too_many_login_attempts = not tlog.allow(os.environ['REMOTE_ADDR'], 'login')
    if should_print_login_form:
        if not too_many_login_attempts:
            logger.debug('Printing login form')
            #print '  <meta name="viewport" content="width=500, initial-scale=1.0"/> <!-- maximum-scale=1.0, user-scalable=0,"/>  -->'
            print '  <meta name="viewport" content="width=device-width, initial-scale=1.0 maximum-scale=2.0, user-scalable=1"/>'
            print constants.login_form_validator_text
            if len(username):
                default_focus_text = ' OnLoad="document.loginform.pass.focus();"'
            else:
                default_focus_text = ' OnLoad="document.loginform.user.focus();"'
        else:
            default_focus_text = ''
            print '<strong>Too many failed login attempts.</strong>'
    else:
        print '  <meta name="viewport" content="width=500, initial-scale=1.0"/> <!-- maximum-scale=1.0, user-scalable=0,"/>  -->'
        print constants.html_head_table_style
        default_focus_text = ' OnLoad="document.filterform.filter.focus();"'

    print constants.close_head_text % (default_focus_text,)

    #
    # Begin body
    #
    if not should_print_login_form:
        print constants.table_sorter_headers_text
    print constants.html_body_prefix_text

    if len(special_message):
        print special_message

    if should_print_login_form:
        if not too_many_login_attempts:
            print '<div style="position:absolute; top:25%; margin-top: -48px; left:50%; margin-left: -203px">'
            if should_print_failed_login:
                print "<p><b>Sorry! That username or password is incorrect.</b></p>"
                if len(verify_msg):
                    print "<p>%s</p>" % verify_msg
            print_login_form(username)
            print '</div>'
        print constants.credits_text
    else:
        print '<div style="text-align:right">%s <a href="index.py?do=logout">logout</a></div><br />' % username
#        print '<div class="note"><strong>TIP:</strong> Sort multiple columns by holding down the <strong>shift</strong> key when clicking another header.</div><br />'
        print constants.table_header
        for id, type, desc, user, pwd, url, cust, ts, notes in rows:
            print "<tr>"
            print "    <td><a href=\"edit.py?id=%d\">Edit</a></td>" % int(id)
            print "    <td>%s</td>" % (type)
            if url.startswith('http'):
                print "    <td><a href=\"%s\">%s</a></td>" % (url, desc)
            else:
                print "    <td>%s</td>" % (desc)
            date = '<span style="color:lightgrey">%s</span>' % (time.strftime("%Y-%m-%d", time.localtime(float(ts))),)
            print "    <td>%s</td>\n    <td class=\"m\">%s</td>\n    <td>%s</td>\n    <td>%s %s</td>" % (user, pwd, cust, notes, date)
            print "</tr>"
        print constants.table_footer

    print constants.html_footer_text
    logging.debug('Done. Printed footer.')


