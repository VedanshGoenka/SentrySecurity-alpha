#!/bin/sh

showEvents()
{
	echo "select e.eventId, e.startTime, e.endTime, e.startTimeMillis, e.endTimeMillis, z.name from Events e join Zones z on e.zoneId = z.zoneId;" |
	/usr/bin/sqlite3 data/sentryDB.sqlite3
}

while [ 1 ]
do
	showEvents
	echo "-------------------------------------------------------------"
	sleep 5
done

