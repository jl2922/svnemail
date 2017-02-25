#!/usr/bin/env python
import os
import re
import smtplib
import subprocess
import sys
from email.mime.text import MIMEText

URL = 'svn://qmc4.physics.cornell.edu/programs/sqmc'
INFO_CMD = 'svn info --username JunhaoLi %s' % URL
MSG_CMD_PREFFIX = 'svn log --username JunhaoLi %s -r ' % URL

RECORD_FILE = os.path.dirname(os.path.realpath(__file__)) + '/record.txt'

FROM = 'junhao@qmc8.physics.cornell.edu'
TO = ['streaver91@gmail.com']
SUBJECT_TPL = 'New svn commit to sqmc (r%d): %s'

def get_content(filepath):
    f = open(filepath, 'r')
    content = f.read()
    f.close()
    return content

def set_content(filepath, content):
    f = open(filepath, 'w')
    content = f.write(content)
    f.close()
    return content

def send_email(user, to, subject, body):
    email = MIMEText(body)
    email['Subject'] = subject
    email['From'] = user
    email['To'] = ', '.join(to)
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(user, to, email.as_string())
        server.quit()
        print 'Message sent.'
    except:
        print 'Unable to send message.'
        print 'Unexpected error:', sys.exc_info()[0]
        exit(1)

def main():
    # Find latest revision.
    info = subprocess.Popen(
        INFO_CMD, shell=True, stdout=subprocess.PIPE).stdout.read()
    info = info.splitlines()
    latest_revision = int(re.search('\d+', info[5]).group(0))
    print 'Latest revision:', latest_revision

    # Check revision on local record file.
    record_revision = int(get_content(RECORD_FILE))
    print 'Record revision:', record_revision

    # Obtain logs and send emails for each new revision and update local record.
    for r in range(record_revision + 1, latest_revision + 1):
        print '\nProcessing revision:', r

        # Obtain log message.
        message_cmd = MSG_CMD_PREFFIX + str(r)
        message = subprocess.Popen(
            message_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

        # Send email
        message_abbr = message.splitlines()[3]
        if len(message_abbr) > 30:
            message_abbr = message_abbr[0:30] + '...'
        subject = SUBJECT_TPL % (r, message_abbr)
        send_email(FROM, TO, subject, message)

        # Update record file.
        set_content(RECORD_FILE, str(r) + '\n')

if __name__ == '__main__':
    main()
