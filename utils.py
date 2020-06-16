# All non-database specific functions.
# Used for Project-wide functions.

import argparse
import imaplib
import os
import smtplib
import time
from datetime import datetime, timedelta
from os import path

import pytz
from pytz import timezone
from twilio.rest import Client

from defaultvalues import *

imap_host = 'imap.gmail.com'
imap_user = EMAIL_USERNAME
imap_pass = EMAIL_PASSWORD

__ImapFromFilter = ['(FROM "%s")', 'OR (From "%s") (From "%s")']

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)  # defaultvalues.py

# Debug Levels => Higher Number = More Verbose.
DEBUG = 4
INFO = 3
WARN = 2
ERROR = 1

# Manually set Project-wide debugLevel, can be overridden in some scripts through --debug (newDebugLevel).
debugLevel = WARN
_debugLevelToString = {ERROR: 'ERROR', WARN: 'WARN', INFO: 'INFO', DEBUG: 'DEBUG'}
_debugStringToLevel = {'ERROR': ERROR, 'WARN': WARN, 'INFO': INFO, 'DEBUG': DEBUG}


def debug(message, level):
    """
    Only outputs messages if debugLevel is at or above level.
    """
    if level <= debugLevel:
        print('%s: %s' % (_debugLevelToString[level], message))


def addDebugArgument(argParser):
    """
    Add --debug as a commandline argument with choices.\n
    :param argParser: argparse.ArgumentParser(description='')
    """
    argParser.add_argument("--debug", choices=['error', 'warn', 'info', 'debug'],
                           help="Change debug level")


def setDebugOverride(parsedArgs):
    """
    Set the global debugLevel if overridden by user.\n
    :param parsedArgs: argParser.parse_args()
    """
    global debugLevel
    if parsedArgs.debug is not None:
        debugLevel = _debugStringToLevel.get(str(parsedArgs.debug).upper(), debugLevel)


def setOptionalFlags(description):
    """
    Fully creates/detects/overrides global debugLevel.
    """
    argParser = argparse.ArgumentParser(description=description)
    addDebugArgument(argParser)
    parsedArgs = argParser.parse_args()
    setDebugOverride(parsedArgs)


def listOnNewline(listToPrint):
    """
    Takes a list and formats into a multi-line string.\n
    :return: Multi-line string for printing or parsing
    """
    strOutput = str()
    for line in listToPrint:
        strOutput = strOutput + line + '\n'
    return strOutput


def timeNow(micro=False):
    """
    Get the time right now. Defaults to seconds, can get microseconds.
    """
    if micro:
        dateFormat = '%Y-%m-%d %H:%M:%S.%f'
    else:
        dateFormat = '%Y-%m-%d %H:%M:%S'
    date = datetime.now(tz=pytz.utc)
    now = date.astimezone(timezone('US/Pacific'))
    return now.strftime(dateFormat)


def strpTime(strTime):
    """
    Change a string with correct format to a datetime object.
    """
    if strTime is None:
        return None
    return datetime.strptime(strTime, '%Y-%m-%d %H:%M:%S')


def timeNowMillis():
    """
    Milliseconds since Epoch
    """
    return int(datetime.now().timestamp() * 1000)


def timeOffset(micro=False, days=0, mins=0, secs=0, millis=0):
    """
    Time after specified delay (+/-) can get microseconds in PST.
    """
    if micro:
        dateFormat = '%Y-%m-%d %H:%M:%S.%f'
    else:
        dateFormat = '%Y-%m-%d %H:%M:%S'
    date = datetime.now(tz=pytz.utc)
    now = date.astimezone(timezone('US/Pacific'))
    timeSoon = now + timedelta(days=days, minutes=mins, seconds=secs, milliseconds=millis)
    return timeSoon.strftime(dateFormat)


def timeToStr(millis):
    """
    Milliseconds since Epoch to timeNow in PST
    """
    return datetime.fromtimestamp(millis / 1000, timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')


def timeToStrSimplified(millis):
    """
    Milliseconds since Epoch to timeNow in PST, only with hours and minutes.
    """
    return datetime.fromtimestamp(millis / 1000, timezone('US/Pacific')).strftime('%H:%M')


def timeDelta(end, start):
    """
    Return elapsed time from start to end. If elapsed time > 60 sec, returns minutes.\n
    :param end: type -  datetime object
    :param start: type - datetime object
    """
    delta = end - start
    seconds = int(delta.seconds)
    mins = int(seconds / 60)
    if mins == 0:
        formatted = '%d sec' % seconds
    else:
        formatted = '%d min %d sec' % (mins, seconds % 60)
    return formatted


def notify(message):
    """
    Send a message using Twilio
    """
    try:
        localtime = time.asctime(time.localtime(time.time()))
        msg = localtime + ": %s" % message
        client.messages.create(
            body=msg,
            from_=TWILIO_NUMBER,
            to=SMS_NUMBER
        )
    except Exception as ex:
        debug("Notify failed with Exception:\n%s" % str(ex), ERROR)


def readEmail(senders, subject=True):
    """
    Reads all emails from approved senders and returns dict with the index and subject.\n
    :param senders: List with acceptable senders
    :param subject: Whether to parse for subject, default: True
    :return: imapHandle (passed through, Dict with Index as key and un-formatted subject as value.
    """
    nSenders = len(senders)
    if nSenders > len(__ImapFromFilter):
        raise Exception
    elif nSenders == 1:
        fromFilter = str(__ImapFromFilter[nSenders - 1] % senders[0])
    else:
        fromFilter = str(__ImapFromFilter[nSenders - 1] % (senders[0], senders[1]))
    # connect to host using SSL
    imap = imaplib.IMAP4_SSL(imap_host)
    # login to server
    imap.login(imap_user, imap_pass)
    imap.select('Inbox')
    status, msgNum = imap.search(None, fromFilter)
    debug(status, INFO)
    debug(msgNum, DEBUG)
    emailSubjects = dict()
    if subject:
        for msgIndex in msgNum[0].split():
            fetchStatus, emailContent = imap.fetch(msgIndex, '(BODY[HEADER.FIELDS (Subject)])')
            emailSubjects[msgIndex] = emailContent[0][1].decode("utf-8")
    return imap, emailSubjects


def sendMail(recipient, subject, content):
    """
    Usage: "sender.sendMail()"\n
    Sample Parameters:\n
    :param recipient: 'johndoe@gmail.com'
    :param subject: 'Email Subject'
    :param content: 'Message for John Doe'
    """
    # Create Headers
    headers = ["From: " + EMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
               "MIME-Version: 1.0", "Content-Type: text/html"]
    headers = "\r\n".join(headers)

    # Connect to Email Server
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo()

    # Login to Email
    session.login(EMAIL_USERNAME, EMAIL_PASSWORD)

    # Send Email & Exit
    session.sendmail(EMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
    session.quit()


def setAbsolutePath(relativePath, pathVars):
    """
    Look for the file specified by relativePath in all environment variables in the pathVars list and return the one
    that corresponds to an existing file.\n
    :return: an absolute path of the file
    """
    pathsTried = list()
    for homeVar in pathVars:
        if homeVar in os.environ:
            pyHome = os.environ[homeVar]
            absolutePath = os.path.join(pyHome, relativePath)
            if path.exists(absolutePath):
                return absolutePath
            else:
                pathsTried.append(absolutePath)
    debug("Could not find file %s in any specified PATH Variables: %s" % (relativePath, pathVars), INFO)
    return None
