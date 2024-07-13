#!/home/dblume/opt/python-3.9.6/bin/python3
#
# http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/

import os
import sys
import filelock
import time
import codecs
import smtplib
from collections import defaultdict
import smtp_creds
import logging

class Transaction_log_exception( Exception ):
    pass


def send_email(subject, message, toaddrs,
        fromaddr='"secure.dlma %s" <%s>' % (os.path.basename(__file__), smtp_creds.user)):
    """ Sends Email """
    smtp = smtplib.SMTP(smtp_creds.server, port=smtp_creds.port)
    smtp.login(smtp_creds.user, smtp_creds.passw)
    smtp.sendmail( fromaddr,
                   toaddrs,
                   "Content-Type: text/plain; charset=\"us-ascii\"\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\n%s" % \
                   ( fromaddr, ", ".join( toaddrs ), subject, message ) )
    smtp.quit()


def Map_ip(ip):
    if ip == '50.224.7.235':  # was '12.155.29.254', '12.155.29.1'
        ip = 'work'
    elif ip == '67.160.193.38':
        ip = 'home'
    elif ip.startswith('128.195.97'):
        ip = 'uci'
    return ip


class Transaction_log(object):
    """ An object to query th existing log and to add new logs. """
    def __init__(self, filename, pylog=None):
        """ Prepare the Transaction log """
        self.filename = filename
        self.logs = []
        self.pylog = pylog
        if self.pylog is not None:
            self.pylog.debug('In Transaction_log __init__')
        if os.path.exists(self.filename):
            try:
                with filelock.FileLock(filename) as lock:
                    f = codecs.open(self.filename, 'r', 'utf-8')
                    try:
                        self.logs = f.readlines()
                    finally:
                        f.close()
            except filelock.FileLockException as e:
                pass

    def allow(self, ip_addr, action):
        """ return whether or not the action should be allowed """
        if action == 'login':
            ip = Map_ip(ip_addr)
            cur_time = time.localtime()
            failed_logins_by_ip = defaultdict(list)
            consecutive_failed_login_count = 0
            for line in self.logs:
                log_time_string, log_ip, log_action, log_detail = line.rstrip('\n').split('\t')
                if log_action == 'login':
                    if log_detail.split(' ')[-1].find('fail') != -1:
                        failed_logins_by_ip[log_ip].append(time.strptime(log_time_string, '%Y-%m-%d, %H:%M:%S'))
                        consecutive_failed_login_count += 1
                    else:
                        consecutive_failed_login_count = 0

            too_many_recent_failed_logins = False
            max_number_failed_logins = 8
            if consecutive_failed_login_count > max_number_failed_logins:
                log_time_string, unused = self.logs[max_number_failed_logins-1].split( '\t', 1 )
                if time.time() - time.mktime( time.strptime( log_time_string, '%Y-%m-%d, %H:%M:%S' ) ) < 120:
                    too_many_recent_failed_logins = True

            if len(failed_logins_by_ip[ip]) > 5 or too_many_recent_failed_logins:
                if time.time() - time.mktime(failed_logins_by_ip[ip][4]) < 60:
                    cur_time = time.strftime('%H:%M:%S, %Y-%m-%d', time.localtime())
                    try:
                        send_email('secure.dlma.com ' + action + ' disallowed',
                                   # 'At ' + cur_time  + ' http://www.magic-net.info/my-ip-and-city-information.dnslookup?fname=' + \
                                   # ip + '&Find+IP+location=Find+IP\r\nSee the logs at: https://secure.dlma.com/log.txt\r\nAction attempted: ' \
                                   # + action + '.\r\n',
                                   'At ' + cur_time  + ' http://www.iplocation.net/index.php?query=' + ip_addr + \
                                       '\r\nSee the logs at: https://secure.dlma.com/log.txt\r\nAction attempted: ' + \
                                       action + '.\r\n',
                                       ('david.blume@gmail.com', 'daliblume@gmail.com'))
                    except Exception as e:
                        print("Could not send email to notify you of the exception. :(")
                    return False
        return True


    def log(self, ip, action, detail):
        """ log attempt
            action can be: "login", "logout", "edit", "delete", """
        # Just keep the last 200 or so
        self.logs = self.logs[:200]
        ip = Map_ip( ip )
        self.logs.insert( 0, "%s\t%s\t%s\t%s\n" % ( time.strftime( '%Y-%m-%d, %H:%M:%S', time.localtime() ), \
                                                     ip,
                                                     action,
                                                     detail ) )
        try:
            with filelock.FileLock( self.filename ) as lock:
                f = codecs.open( self.filename, 'w', 'utf-8' )
                try:
                    f.writelines( self.logs )
                finally:
                    f.close()
        except filelock.FileLockException as e:
            pass

if __name__=='__main__':
    localdir = os.path.abspath( os.path.dirname(sys.argv[0]))
    tlog = Transaction_log(os.path.join(localdir, 'test_log.txt'))
    print("tlog.allow", tlog.allow('10.100.12.131', 'login'))
    tlog.log('10.100.12.131', 'login', 'fail')
    tlog.log('10.100.12.131', 'login', 'fail')
    tlog.log('10.100.12.131', 'login', 'fail')
    print("Done.")

