# Database initialization values
zoneDict = {1: 'Zone 1', 2: 'Zone 2', 3: 'Zone 3', 4: 'Zone 4',
            5: 'Zone 5', 6: "Zone 6", 7: 'Zone 7', 8: 'Zone 8'}

groupDict = {1: 'Group 1', 2: 'Group 2', 3: 'Group 3', 4: 'Group 4'}

groupedZones = {1: [1], 2: [1, 2, 3, 4], 3: [1, 2, 3, 4, 6, 7, 8], 4: [5, 6]}  # {GroupDict: [listOfZones]}

# Values in Seconds
activationDelay = 60
notificationGap = 60
openDuration = 60  # Not enabled yet.

# Format: {'alarmName':('groupName', int(activationDelay), int(notificationGap), int(openDuration))}
alarmDict = {'Alarm 1': ('Group 1', 120, 180, 30),
             'Alarm 2': ('Group 2', activationDelay, notificationGap, openDuration),
             'Alarm 3': ('Group 3', 0, notificationGap, openDuration),
             'Alarm 4': ('Group 4', 0, notificationGap, openDuration),
             'Alarm 5': ('Group 4', 0, notificationGap, openDuration)}

# This is the path of database file relative to the python code
databasePath = 'database/sentryDB.sqlite3'

# Time format
formatHH_MM = '%I:%M %p'

# Configurable Values

# Note: Must "Allow Less Secure Apps" in Settings.
EMAIL_USERNAME = 'email@email.com'  # Email to send from
EMAIL_PASSWORD = 'password'  # Email's password
SMTP_SERVER = 'smtp.gmail.com'  # Email Server
SMTP_PORT = 587  # Server Port

EMAIL_RECIPIENT = 'recipient@email.com'
EMAIL_SUBJECT = "Event Triggered On Sentry"
EMAIL_SENDERS = ['recipient@email.com', 'recipient2@email.com']

TWILIO_NUMBER = '+1555555555'
SMS_NUMBER = '+15555555555'

# Randomized
TWILIO_ACCOUNT_SID = "H8m0em7KGj4e92r9TIVm6h47ANUGj7s8ru"
TWILIO_AUTH_TOKEN = 'USb5x2xPV8EwCfQ1vdt4zzHeeI2sW01P'

try:
    from private.defaultvalues import *
except ModuleNotFoundError:
    pass
