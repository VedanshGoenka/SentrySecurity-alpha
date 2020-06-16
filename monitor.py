# Runs 24/7/365
# Read values over serial, from Arduino, parses and updates database accordingly.
# Accepts --debug as a commandline argument

import re

import serial

from alarmDB import *

_dataNew = dict()
_dataOld = dict()
_openedZones = dict()

ser = serial.Serial('/dev/ttyACM0', 9600)  # Serial Port and Baud rate

debug('Connected', INFO)


def qualityCheck(item):
    """
    Check if voltage matches specified format.
    """
    expectedFormat = re.match('(\d[:]\d[.][0-9]+)', item)
    if not expectedFormat:
        debug('Bad data: ' + item + '!', WARN)
    return expectedFormat


def readNextRecord():
    """
    Read all current voltage values.\n
    :return: Format: {zoneId : voltage}
    """
    newData = dict()
    while True:
        # Put record into parsed dict
        record = ser.readline()
        debug(record, DEBUG)
        try:  # Change bytes file format to utf-8
            lst = record.decode('utf-8').strip("\r\n").split(',')
        except UnicodeDecodeError:  # Discard errors
            debug(record, ERROR)
            continue
        debug(lst, DEBUG)
        for item in list(filter(None, lst)):  # Add all values from list to a dictionary, sorting out None
            if not qualityCheck(item):
                continue
            zone, voltage = tuple(map(float, item.split(':')))
            newData[int(zone)] = voltage
        if len(newData) == len(zoneDict):  # If all events have been captured - success
            return newData
        else:  # If partial data - read again
            newData.clear()


def mainMonitor():
    """
    Monitor all zones
    """
    try:
        setOptionalFlags('This script is used to monitor zone activity and update the database')
        print('Starting Detection')
        while True:
            nextRecord = readNextRecord()
            openZones = readOpenZones()
            debug('Data Captured', DEBUG)
            for zone, voltage in nextRecord.items():  # Read each record
                nowMillis = timeNowMillis()
                zoneName = zoneDict.get(zone)
                openZoneState = openZones.get(zone)
                if voltage >= 2.5:  # If the zone has been tripped.
                    if openZoneState is None:  # Zone is open with no existing entry, create a new open entry
                        recordZoneOpen(nowMillis, zone)
                        debug('New Item Created: ' + zoneName, INFO)
                    else:  # Zone is open, but an entry exists
                        debug('Zone: ' + zoneName + ' is already open', INFO)
                else:  # The zone isn't tripped
                    if openZoneState is not None:  # If as open entry exists
                        zoneOpenTime = openZoneState[1]
                        openZoneEventId = openZoneState[0]
                        if zoneOpenTime is None:  # A zone should never be open without a start time, fix it!
                            addMissingStartTime(nowMillis, openZoneEventId)
                            debug('New Item Created: ' + zoneName + ' w/ Error', ERROR)
                        else:  # Zone is open, but voltage is low, so mark existing entry closed
                            recordZoneClose(nowMillis, openZoneEventId)
                            debug('Zone: ' + zoneName + ' Closed', INFO)
    except KeyboardInterrupt:
        quit('\nExited')


if __name__ == "__main__":
    mainMonitor()
