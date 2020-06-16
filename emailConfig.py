# Reads the subject of emails from authorised senders and executes commands
# Run periodically through the crontab
import distutils
import re
from distutils import util
from enum import Enum

from activeConfig import modifyAlarms
from alarmDB import *
from utils import *

allowedSenders = EMAIL_SENDERS

mergedDict = dict()
emailMessages = list()


def merge(dict1, dict2):
    """
    Gives a single dictionary with all the most recent commands.
    """
    return dict2.update(dict1)


class CommandStatus(Enum):
    """
    Status of parseAlarmCommands
    """
    OK = 1
    HELP = 2
    ERROR = 3
    IGNORE = 4


# return (Command.OK, dict) or (Command.HELP, None), (....)
def parseAlarmCommands(allCommandDict, logs):  # parseAllEmails
    """
    Parses the commands from an email and reports syntactical errors.\n
    :param allCommandDict: Dict with the email's subject separated into words (indexed by email index)
    :param logs: Messages for the email
    :return: Tuple with CommandStatus, Info/Data
    """
    returnLst = list()
    for emailIndex, aCommand in allCommandDict.items():
        numberArguments = len(aCommand)
        message = ' '
        if numberArguments == 0 or str(aCommand[0]).lower() == 'help':  # User needs help
            logs.insert(0, 'Usage: alarm ("alarmName" "on/off")...')
            debug('Asked for syntax', INFO)
            returnLst.append((CommandStatus.HELP, emailIndex, None))
        elif numberArguments % 2 == 1:  # Number of arguments must be even
            error = 'Malformed Syntax, wrong number of arguments'
            logs.append('ERROR -- %s: "%s"' % (error, message.join(aCommand)))
            returnLst.append((CommandStatus.ERROR, emailIndex, None))
        else:
            index = 0
            allAlarms = readAllAlarms_Name()
            outputCommand = dict()
            error = None
            for _ in range(0, int(numberArguments / 2)):  # Runs the number of arguments given
                alarmName = str(aCommand[index]).capitalize()
                if allAlarms.get(alarmName, None) is None:  # Check if alarmName is a defined alarm
                    error = "Alarm name doesn't exist"
                    debug(error, WARN)
                    logs.append('ERROR -- %s: "%s"' % (error, message.join(aCommand)))
                    returnLst.append((CommandStatus.ERROR, emailIndex, None))
                    break
                try:
                    alarmSetting = bool(distutils.util.strtobool(aCommand[index + 1]))
                except ValueError:  # If alarmSetting is not a boolean value
                    error = 'Non-Boolean Value'
                    debug(error, WARN)
                    logs.append('ERROR -- %s: "%s' % (error, message.join(aCommand)))
                    returnLst.append((CommandStatus.ERROR, emailIndex, None))
                    break
                outputCommand[alarmName] = alarmSetting
                index += 2
            if error is None:
                logs.append('OK -- "%s"' % message.join(aCommand))
                returnLst.append((CommandStatus.OK, emailIndex, outputCommand))
    return returnLst


def emailFormat(log):
    """
    Formats the list to an email
    """
    message = str()
    for event in log:
        message = message + str(event) + '<br/>'
    debug(message, DEBUG)
    return message


def parseEmailSubjects(subjectDict, prefix):
    """
    Takes the non-formatted email subject and extracts message for parsing.\n
    :param prefix: The command used to specify the device ('alarm'/'sentry')
    :param subjectDict: Imap email index and Email Subject
    :return: Email's subject
    """
    formattedSubjects = dict()
    regex = 'subject: ' + prefix.lower() + ' (.+)\r'
    for index, email in subjectDict.items():
        debug(email, DEBUG)
        subjectMessage = re.findall(regex, email.lower())
        if len(subjectMessage) > 0:
            msgLst = str(subjectMessage[0]).split()
            debug(msgLst, INFO)
            formattedSubjects[index] = msgLst
    return formattedSubjects


def archiveEmail(imapServer, mailIndex):
    """
    Archive emails (that have already been parsed).\n
    :param imapServer: "imaplib.IMAP4_SSL(imap_host)"
    :param mailIndex: Imap email index
    """
    imapServer.store(mailIndex, '+FLAGS', '\\Deleted')  # Use imapServer.expunge() for deletion
    message = 'Email moved to archive'
    debug(message, INFO)


def sendConfirmationEmail(message, changeLog, emailRecipient, openZones):
    """
    Sends confirmation email.\n
    :param message: List with email body
    :param changeLog: Dictionary with all actions
    :param emailRecipient: Email Recipient
    :param openZones: Warning for which zones are open
    """
    divider = '-----------------------------------------'
    emailMessages.insert(1, divider)
    message.append(divider)
    message.append('New Active Alarms: %s' % list(readActiveAlarms().keys()))
    message = message + changeLog
    if len(openZones) > 0:
        message = message + [divider, 'Warning: The following alarms have open zones -', str(openZones)]
    debug(message, INFO)
    sendMail(emailRecipient, 'Sentry: Command Execution Log', emailFormat(message))
    print('Email has been sent')


if __name__ == "__main__":
    setOptionalFlags("This script searches each email's subject for commands and executes them")
    emailMessages = list()
    imapHandle = None
    try:
        imapHandle, allSubjects = readEmail(allowedSenders)
        debug(allSubjects, INFO)
        parsedSubjects = parseEmailSubjects(allSubjects, "alarm")
        debug(parsedSubjects, INFO)
        handledMessageLst = parseAlarmCommands(parsedSubjects, emailMessages)
        if len(handledMessageLst) > 0:  # Send email & update database
            mergedDict = dict()
            for exitStatus, messageIndex, executeCommands in handledMessageLst:
                archiveEmail(imapHandle, messageIndex)
                if exitStatus == CommandStatus.OK:
                    merge(executeCommands, mergedDict)
            emailMessages.insert(0, 'Currently Active Alarms: %s' % list(readActiveAlarms().keys()))
            sendConfirmationEmail(emailMessages, modifyAlarms(mergedDict), EMAIL_RECIPIENT,
                                  readOpenZonesInActiveAlarms())
    except Exception as e:
        print(e)
    if imapHandle is not None:
        imapHandle.close()
