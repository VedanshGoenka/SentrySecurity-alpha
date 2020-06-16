# This is used with commandline arguments in order to turn specific alarms on and off.
# The usage is python(3) activeConfig.py --"AlarmNameHere" true/false.
# Supports multiple arguments.
from distutils.util import strtobool

from alarmDB import *
from utils import *

activeDict = readActiveAlarms()
allAlarms = readAllAlarms_Name()


def isActive(whichAlarm, activeAlarms):
    """
    Check to see whether the specified alarm (whichAlarm) is currently active.
    """
    if activeAlarms.get(whichAlarm, False):
        return True
    else:
        return False


def parseActiveConfig():
    """
    Looks for commandline arguments and returns formatted dictionary.
    """
    parsedDict = dict()
    argParser = argparse.ArgumentParser(description="""
            This script is used to turn on and off active alarms.
            """)
    addDebugArgument(argParser)  # Add argument --debug
    for alarm in allAlarms:  # Iteratively add all alarms from database as an accepted argument.
        alarm = str(alarm).lower()
        argParser.add_argument(("--%s" % alarm), type=strtobool,
                               help="Setting Alarm: %s on/off." % alarm)
        debug('Alarm %s has been defined' % alarm, DEBUG)
    debug('All entries defined', DEBUG)
    parsedArgs = argParser.parse_args()  # Parse all arguments from commandline (alarms and debug)
    setDebugOverride(parsedArgs)  # Set debug level, if --debug is specified
    for alarmName in allAlarms:
        parsedDict[alarmName] = getattr(parsedArgs, str(alarmName).lower())
    return parsedDict


def modifyAlarms(parsedDict):
    """
    Takes formatted data and makes changes to the database.\n
    :param parsedDict: Format: {'Away': True, 'Stay': False}
    :return: 'No changes' or List of changes
    """
    log = list()
    if len(parsedDict) == 0:
        log.append('No changes were made to the database')
    else:
        for alarmName, alarmState in parsedDict.items():
            activationTime = timeOffset(secs=readNotificationGap(alarmName))  # timeNow + notifyGap = activationTime
            alarmId = allAlarms[alarmName]
            if alarmState == 1:  # User has turned on the alarm
                if isActive(alarmName, activeDict):  # If the alarm is already active
                    message = '%s is already active' % alarmName
                    log.append(message)
                else:  # Alarm Activated/ New Entry
                    activateAlarm(alarmId, activationTime)
                    message = '%s has been activated' % alarmName
                    log.append(message)
            elif alarmState == 0:  # User has turned off the alarm
                if isActive(alarmName, activeDict):  # Alarm Deactivated/ Entry Closed
                    deactivateAlarm(alarmId)
                    message = '%s has been deactivated' % alarmName
                    log.append(message)
                else:  # If the Alarm is inactive
                    message = "%s is already deactivated" % alarmName
                    log.append(message)
            # Don't process newAlarmState is None
    return log


if __name__ == "__main__":
    print('Currently Active Alarms: %s' % list(activeDict.keys()))
    _log = modifyAlarms(parseActiveConfig())
    if len(_log) > 0:
        print(listOnNewline(_log))
        print('New Active Alarms: %s' % list(readActiveAlarms().keys()))
    else:
        print('No Changes were made to the database')
    _openZones = readOpenZonesInActiveAlarms()  # Warn the user which alarms have been activated, but zones are open.
    if len(_openZones) > 0:
        print('Warning: The following alarms have open zones -')
        print(_openZones)
