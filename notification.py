# This script sends a notification with all the events between lastNotificationTime and nextNotificationTime
# It is recommended to put this script in the Cron-tab to call at an interval.
# The frequency at which notifications are sent is dependent on notificationGap in "defaultvalues.py"
# Accepts --debug as a commandline argument

from alarmDB import *
from utils import *


def buildTextMessage(messageGroup):
    """
    Format textMessage for delivery.\n
    :param messageGroup: Format: {alarmName:[int(notificationGap), messageToSend1, messageToSend2...]}
    :return: Multi-line formatted string for delivery
    """
    sendMessage = str()
    lookupTable = readAllAlarms_ID()
    for key, lst in messageGroup.items():
        sendMessage = sendMessage + lookupTable[key] + ':\n'
        for item in lst:
            if type(item) is int:  # Ignore the notificationGap values
                continue
            sendMessage = sendMessage + item + '\n'
    return sendMessage


def buildEmailMessage(messageGroup):
    """
    Format email for delivery.\n
    :param messageGroup: Format: {alarmName:[int(notificationGap), messageToSend1, messageToSend2...]}
    :return: Multi-line formatted string for delivery
    """
    sendMessage = str()
    lookupTable = readAllAlarms_ID()
    for key, lst in messageGroup.items():
        sendMessage = sendMessage + lookupTable[key] + ': <br/>'
        for item in lst:
            if type(item) is int:  # Ignore the notificationGap values
                continue
            sendMessage = sendMessage + item + '<br/>'
    return sendMessage


def mainNotification():
    """
    Send any notifications if available
    """
    try:
        setOptionalFlags('This script sends notifications for active alarms.')
        activeAlarmEvents = readActiveAlarmsEvents()
        debug(activeAlarmEvents, DEBUG)
        debug(len(activeAlarmEvents), DEBUG)
        messages = dict()
        if len(activeAlarmEvents) > 0:  # If there are no events to notify about, quit()
            for values in activeAlarmEvents:
                alarmName = values[0]
                zoneName = values[1]
                zoneId = values[2]
                startTime = strpTime(values[3])  # Format from string to datetime object
                endTime = strpTime(values[4])
                gapNotification = values[5]
                eventId = values[6]
                lastNotificationTime = strpTime(values[7])
                alarmId = values[8]
                minOpenDuration = values[9]  # TODO: USE minOpenDuration and create test cases.
                if not messages.get(alarmId, False):  # Create new list nested in messages' dictionary for unique alarms
                    messages[alarmId] = list()
                    messages[alarmId].append(gapNotification)  # set first value in list to the notificationGap
                if startTime >= lastNotificationTime:  # Event started after the lastNotificationTime
                    if endTime is None:  # Event hasn't been closed
                        eventMessage = '%s - %s is open' % (startTime.strftime(formatHH_MM), zoneName)
                        messages[alarmId].append(eventMessage)
                        debug(eventMessage, DEBUG)
                    else:  # Event has closed
                        eventMessage = ('%s - %s was open for %s' % (startTime.strftime(formatHH_MM), zoneName,
                                                                     timeDelta(endTime, startTime)))
                        messages[alarmId].append(eventMessage)
                        debug(eventMessage, DEBUG)
                else:  # Event started before lastNotificationTime
                    if endTime is None:  # Cannot Occur due to fetchall() filters
                        debug('Error - SQL Fetch Filter Failed', ERROR)
                    else:  # Previously Open Event Closed
                        eventMessage = '%s - %s has been closed after %s' % (
                            endTime.strftime(formatHH_MM), zoneName,
                            timeDelta(endTime, startTime))
                        messages[alarmId].append(eventMessage)
                        debug(eventMessage, DEBUG)

            try:  # Send Email
                msg = buildEmailMessage(messages)
                debug(msg, INFO)
                sendMail(EMAIL_RECIPIENT, EMAIL_SUBJECT, msg)
            except Exception as failure:  # Send Text Message
                debug(str(failure), ERROR)
                msg = buildTextMessage(messages)
                debug(msg, INFO)
                notify(msg)

            updateAlarmNotificationTime(messages)  # Move lastNotificationTime and nextNotificationTime forwards

        else:
            print('No New Events or Just Sent Events')

    except KeyboardInterrupt:
        quit('\n Exited before any notification was sent')


if __name__ == "__main__":
    mainNotification()
