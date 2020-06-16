# These are all the functions that execute sqlite queries.
# The cursor object is created before every event, and the connection is committed after.

import sqlite3

from utils import *

_absoluteDatabasePath = setAbsolutePath(databasePath, ['PYHOME', 'HOME', 'PWD'])
if _absoluteDatabasePath is None:
    raise FileNotFoundError("Database file not found: %s" % databasePath)

conn = sqlite3.connect(_absoluteDatabasePath)


def readOpenZones():
    """
    Returns a dictionary with {zoneID : (eventId, startTime)} for zones that don't have an endTime.
    """
    cur = conn.cursor()
    cur.execute('Select eventId, startTime, zoneId from Events where endTime is Null')
    results = cur.fetchall()
    if len(results) > len(zoneDict):
        debug('Database Error: %d Unclosed Events', ERROR % (len(results)))
    openZones = dict()
    for row in results:
        openZones[row[2]] = (row[0], row[1])
    conn.commit()
    return openZones


def readActiveAlarmsEvents():
    """
    Returns a sorted list of tuples for all new events for active alarms with the format:
    [(alarmName,zoneName,zoneID, startTime, endTime, notificationGap, eventId, lastNotificationTime, alarmId)...]
    """
    cur = conn.cursor()
    cur.execute(
        'SELECT a.name, z.name, z.zoneId, e.startTime, e.endTime, a.notificationGap, e.eventId, '
        'aa.lastNotificationTime, a.alarmId, a.minOpenDuration FROM ActiveAlarms aa JOIN Alarms a USING (alarmId) JOIN '
        'ZoneGroup zg on (a.monitoredGroup = zg.groupId) JOIN Zones z USING (zoneId) JOIN Events e USING (zoneId) WHERE'
        ' (( aa.lastNotificationTime <= e.startTime) OR ( aa.lastNotificationTime <=e.endTime)) AND ('
        'aa.nextNotificationTime <= "%s") ORDER BY a.name ASC, e.startTime ASC ;' % (timeNow()))
    data = cur.fetchall()
    conn.commit()
    return data


def readOpenZonesInActiveAlarms():
    """
    Returns a sorted list of tuples for all open zones, sorted by alarm name (ascending) with the format:
    [(alarmName, zoneName, startTime)...]
    """
    cur = conn.cursor()
    cur.execute(
        'SELECT a.name, z.name, e.startTime FROM ActiveAlarms aa JOIN Alarms a USING (alarmId) JOIN ZoneGroup zg on ('
        'a.monitoredGroup = zg.groupId) JOIN Zones z USING (zoneId) JOIN Events e USING (zoneId) WHERE '
        'e.endTime IS Null ORDER BY a.name ASC;'
    )
    data = cur.fetchall()
    conn.commit()
    return data


def readAllAlarms_ID():
    """
    Returns a dictionary with {alarmId: alarmName}
    """
    cur = conn.cursor()
    cur.execute('SELECT alarmId, name FROM Alarms ORDER BY alarmId ASC')
    table = cur.fetchall()
    alarmTable = dict()
    for items in table:
        alarmTable[items[0]] = items[1]
    conn.commit()
    return alarmTable


def readAllAlarms_Name():
    """
    Returns a dictionary with {alarmName: alarmId}
    """
    cur = conn.cursor()
    cur.execute('SELECT alarmId, name FROM Alarms ORDER BY alarmId ASC')
    table = cur.fetchall()
    alarmTable = dict()
    for items in table:
        alarmTable[items[1]] = items[0]
    conn.commit()
    return alarmTable


def readNotificationGap(alarmName):
    """
    Returns the notificationGap of the specified alarm from the database
    """
    cur = conn.cursor()
    cur.execute('Select notificationGap FROM Alarms WHERE name is "%s"' % alarmName)
    gapNotification = int(cur.fetchone()[0])
    conn.commit()
    return gapNotification


def readActiveAlarms():
    """
    Returns all activeAlarms as a dictionary with {alarmName: alarmId}
    """
    cur = conn.cursor()
    cur.execute('SELECT aa.alarmId, a.name FROM ActiveAlarms aa JOIN Alarms a USING (alarmId) ORDER BY alarmId ASC')
    data = cur.fetchall()
    activeAlarms = dict()
    for items in data:
        activeAlarms[items[1]] = items[0]
    conn.commit()
    return activeAlarms


def updateAlarmNotificationTime(messages):
    """
    Updates database with new lastNotificationTime and nextNotificationTime.\n
    :param messages: Output from notification.py. Dict Format: Key => alarmId, Values => First Value is notificationGap
                        following values are messages.
    """
    cur = conn.cursor()
    for alarmID, events in messages.items():
        gapNotification = events[0]
        updateMsg = 'UPDATE ActiveAlarms SET lastNotificationTime="%s", nextNotificationTime="%s" WHERE alarmId = %d' \
                    % (timeNow(), timeOffset(secs=gapNotification), alarmID)
        debug(updateMsg, DEBUG)
        cur.execute(updateMsg)
    conn.commit()


def recordZoneOpen(startTimeMillis, zoneId):
    """
    Inserts into the database a new event with startTime (str & int) and zone.
    """
    cur = conn.cursor()
    cur.executescript('INSERT INTO Events (startTime, startTimeMillis, zoneId) VALUES ("%s",%d,%d)'
                      % (timeToStr(startTimeMillis), startTimeMillis, zoneId))
    conn.commit()


def addMissingStartTime(startTimeMillis, eventId):
    """
    Updates database with startTime for empty events (error)
    """
    cur = conn.cursor()
    cur.executescript('UPDATE Events SET startTime = "%s", startTimeMillis = %d WHERE eventId = %d'
                      % (timeToStr(startTimeMillis), startTimeMillis, eventId))
    conn.commit()


def recordZoneClose(startTimeMillis, eventId):
    """
    Updates database with endTime to close an event
    """
    cur = conn.cursor()
    cur.executescript(
        'UPDATE Events SET endTime = "%s", endTimeMillis = %d WHERE eventId = %d'
        % (timeToStr(startTimeMillis), startTimeMillis, eventId))
    conn.commit()


def activateAlarm(alarmId, activationTime):
    """
    Inserts into the database a new ActiveAlarm, creates log in AlarmHistory
    """
    cur = conn.cursor()
    now = timeNow()
    cur.execute('INSERT INTO ActiveAlarms (alarmId, activationTime, lastNotificationTime, '
                'nextNotificationTime) VALUES (%d,"%s","%s","%s")' % (
                    alarmId, activationTime, activationTime, activationTime))
    cur.execute('INSERT INTO AlarmHistory (alarmId,startTime) VALUES (%d,"%s")' % (alarmId, now))
    conn.commit()


def deactivateAlarm(alarmId):
    """
    Deletes from the database an existing ActiveAlarm, completes log in AlarmHistory.
    """
    cur = conn.cursor()
    now = timeNow()
    cur.execute('UPDATE AlarmHistory SET endTime = "%s" WHERE alarmId = %d and endTime is Null' %
                (now, alarmId))
    cur.execute('DELETE FROM ActiveAlarms WHERE alarmId = %d' % alarmId)
    conn.commit()


def purgeOldEvents(olderThanDays):
    """
    Prune all events with an endTime before specified days.\n
    :param olderThanDays: Must be a number, can be a float.
    """
    cur = conn.cursor()
    timeDaysAgo = timeOffset(days=-abs(olderThanDays))
    cur.execute('DELETE FROM Events WHERE endTime <= "%s"' % timeDaysAgo)
    conn.commit()
