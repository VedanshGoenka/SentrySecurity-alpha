# WARNING: RUNNING THIS WITH AN EXISTING DATABASE WILL CLEAR EVERYTHING!!!
# Initializes a new database @ databasePath and inserts zones, groups (w/ zone assignments), and alarms.

import sqlite3

from defaultvalues import *

_groupInvertedDict = dict()

conn = sqlite3.connect(databasePath)
cur = conn.cursor()

cur.executescript('''

DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Zones;
DROP TABLE IF EXISTS Groups;
DROP TABLE IF EXISTS ZoneGroup;
DROP TABLE IF EXISTS Alarms;
DROP TABLE IF EXISTS ActiveAlarms;
DROP TABLE IF EXISTS AlarmHistory;

CREATE TABLE Events (
   eventId	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
   startTime	TEXT NOT NULL,
   endTime	TEXT,
   startTimeMillis	INTEGER NOT NULL,
   endTimeMillis	INTEGER,
   zoneId	INTEGER 
);

CREATE TABLE Zones (
   zoneId	INTEGER NOT NULL PRIMARY KEY UNIQUE,
   name	TEXT NOT NULL UNIQUE
);

CREATE TABLE Groups (
   groupId	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
   name	TEXT NOT NULL UNIQUE
);
CREATE TABLE ZoneGroup (
    groupId   INTEGER,
    zoneId    INTEGER,
    PRIMARY KEY (groupId, zoneId),
    FOREIGN KEY(groupId) REFERENCES Groups(groupId),
    FOREIGN KEY(zoneId) REFERENCES Zones(zoneId)
    
);

CREATE TABLE Alarms (
    alarmId  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL UNIQUE,
    monitoredGroup	INTEGER NOT NULL,
    activationDelay INTEGER NOT NULL,
    notificationGap	INTEGER NOT NULL,
    minOpenDuration INTEGER NOT NULL,
    FOREIGN KEY(monitoredGroup) REFERENCES Groups(groupId)
);

CREATE TABLE ActiveAlarms (
    alarmId  INTEGER NOT NULL,
    activationTime   TEXT NOT NULL,
    lastNotificationTime TEXT,
    nextNotificationTime TEXT,
    FOREIGN KEY(alarmId) REFERENCES Alarms(alarmId)   
);

CREATE TABLE AlarmHistory (
    alarmId	INTEGER NOT NULL,
    startTime  TEXT NOT NULL,
    endTime	TEXT,
    FOREIGN KEY(alarmId) REFERENCES Alarms(alarmId)
);


''')
conn.commit()

# Values are from "defaultvalues.py"

for zone, name in zoneDict.items():  # Define all zones
    cur.execute('insert into Zones (zoneId,name) values (%d,"%s")' % (zone, name))

for group, name in groupDict.items():  # Define all groups
    cur.execute('insert into Groups (groupId,name) values (%d,"%s")' % (group, name))
    _groupInvertedDict[name] = group

for group, zoneList in groupedZones.items():  # Assign zones to groups
    for zone in zoneList:
        cur.execute('insert into ZoneGroup (groupId,zoneId) values (%d,%d)' % (group, zone))

for name, values in alarmDict.items():  # Defines all alarms with parameters
    cur.execute('INSERT INTO Alarms (name, activationDelay, monitoredGroup, notificationGap, minOpenDuration) VALUES '
                '("%s",%d,%d,%d,%d)' % (name, values[1], _groupInvertedDict[values[0]], values[2], values[3]))

conn.commit()
conn.close()
