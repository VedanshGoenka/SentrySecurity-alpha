# Sentry: Programmable Monitoring for Existing Residential/Business Alarm Systems

## Problem:

Most of the alarm systems that are pre-installed into houses operate on
a subscription model with the provider. These alarm systems are
internally wired with the sensors installed during construction. This
poses a challenge for many people; if a provider goes out of business,
drops support or the system is old, the software may be seen as the
limiting factor and companies will often offer retrofitting new wireless
solutions. However, in many cases, the hardware is perfectly
functioning. The goal of this project is to breath new life into
outdated alarm systems, avoiding the installation of new wireless
solutions, all while keeping the costs down. Looking at what my house
had to offer, I saw the circuit board for my alarm system (DSC Power 832
PC 5010) in the master bedroom closet. Although there was documentation
for the alarm, these docs are often hard to understand and are not user
friendly, having a quirky design. Additionally, if your system is
misconfigured, it can be very hard to re-configure it without seeking
expert help. Even if you can configure it, you won't get notified when
you are outside unless you buy an expensive monitoring service. Even
then, many companies will prefer newer wireless solutions since these
new sensors come with mobile phone apps that are easy to use. What if
you could get similar ease of use from your existing, old-school, wired
security system?

## Discovery:

Opening up the alarm’s circuit board, there are multiple terminals where
wires go, luckily, there is also a schematic that shows how the alarm
detection works. Probing the terminals and reading the documentation
shows that whenever a window/door/motion sensor is tripped on, an
internal circuit is complete, and the voltage spikes to 10 volts on
exactly one set of marked terminals (often known as a zone).
Additionally, individual windows/zones/sensors are grouped together into
zones, which can be manually mapped by opening each door/window and
checking the various terminals in the switch for a voltage change.


## Solution:

The solution to this problem — dubbed “Sentry” — monitors the opening
and closing of any windows or door from your mobile phone from any
corner of the world, as long as your home internet service and power are
on. You can configure rules so only certain
doors/windows/motion-detectors trigger a notification to your phone, and
you can turn these on/off remotely from your mobile phone or any other
internet connected device (e.g. laptop) as well. Sentry uses an Arduino
Mega to measure the voltage changes, a custom circuit to ensure that the
voltage changes are within the 0-5V range that Arduino supports, and a
Raspberry Pi Zero with internet connectivity for email or SMS
notification. Sentry reads the voltage from the alarm's circuit board to
determine the current state of the zone. The code was developed in
Python and SQLite was used as the database. This makes adding powerful
new capabilities to Sentry quite simple. Additionally, configuration and
current status of the alarms can be configured remotely by sending
emails to Sentry. Sentry solves the problem remarkably well; an alarm
system can be revitalized and given much more functionality for
substantially cheaper than any alternative. Since Sentry is moddable and
open-source, it can have much more features, tailor made for your house
than any existing solution.

#### Benefits:

##### Cost:

- Cost about 50 dollars for initial setup, supports 16 zones.
- Easy to add more zones, either upgrading Arduino or adding more
  Arduinos
- Less expensive than installing new sensors for every window/door

##### Upgradability:

- Open-source, easily moddable
- Features increase and improve over time
- Easy to install and scales to even large buildings.

![sentryDiagram](/Images/sentryDiagram.png)  
Sentry's High Level Design

## Components:

- Raspberry Pi Zero (W)
  - Micro USB to USB A Port/Hub
  - 8+ Gb SD Card
  - Power Supply
    - USB micro adapter for power (5V, 1A)
  - Optional:
    - Ethernet to USB
  - If you want to use Ethernet instead of WiFi for connectivity.
    - Arduino Mega
      - USB A to USB B
  - Circuit Board (for 8 zones)
    - Adafruit Perma-Protoboard
      - <https://www.adafruit.com/product/571>
  - 16 resistors (All 1M Ω unless alarm's circuit board voltage > 10V)
  - 4 Jumper Cables (not for I/O)
  - 12 Jumper cables to Arduino (Output)
  - 2 Female Ethernet Jacks (Input)
    - Guaranteed Compatibility:
      - <https://www.monoprice.com/product?p_id=1044>
    - Can skip the jacks and solder cables.
  - 2.5 in of Ethernet Cabling (without connectors)
    - Will need basic tools for cutting and stripping wires

## Electronics:

### Arduino Usage:

I utilized an Arduino to detect the voltage rather than a voltage sensor
since it was cheaper and the Arduino Mega had 16 built in. The Arduino
is able to detect the voltage through its analog input and represents
the voltage as a value from 0 - 1023, which represents the range from 0V
to 5V.

![Arduino-Mega-Pin-Configuration](/Images/Arduino-Mega-Pin-Configuration.png)
Arduino Mega Pin Configuration

### Circuit:

Since the Arduino only supports 5V, and the alarm circuit outputs ~10V,
a simple voltage reduction circuit was designed. The circuit is a simple
voltage reduction circuit, with two 1MΩ resistors in series and the
input for the Arduino branching out at the intersection of the two
resistors connected. I created 8 of these circuits for each of the
zones.

![singleCircuitDiagram](/Images/singleCircuitDiagram.png)

##### Single Circuit Notes:

- This is one circuit.
- Multiple zones can share a common ground, but not all share the same
  ground
  - You cannot short the ground, at least in my alarm system
- The resistance of the resistor has to do with the ratio between the
  first and second.
  - Higher Ohms are preferred to restrict the current flowing through
    the circuit.
- Each of the common grounds (2-3 zones that share) must be brought to
  different arduino ground pins

### Use of Ethernet Cable (Optional):

I decided to use an ethernet cable to bring the signal from the alarm's
circuit board to the protoboard — the board on which I had built my
circuit. The use of an ethernet cable has a bevy of benefits, this means
that the Arduino’s circuit isn’t tethered to the alarm’s circuit and can
be detached easily. I soldered a female ethernet jack to the board so
that the system can be disconnected easily from the male ethernet cable
connected to the alarm system’s primary circuit board. On one side, the
wires of the ethernet cable are connected to terminals on the alarm's
circuit board and on the other, terminate in the male connector.

![Soldered Protoboard.png](/Images/solderedProtoboard.png) Soldered
Board with Ethernet Jack

### Final Circuit Design & Info:

##### This is the mockup of the circuit that I used when soldering as a guide:

![circuitDiagram.png](/Images/circuitDiagram.png)

##### Final Circuit Notes:

- Purple Dots are where the resistors are connected
- Red dots are where the signal(+) comes from the alarm's circuit board
- Green dots are where the signal (-) returns to the alarm's circuit
  board .
  - Back trace the green dot through its rails to the 2 red dots that it
    originates from; in this configuration, there are 2 reds for each
    green.
    - For example: Bottom (-) green @ 6 is the ground for D7 and E9 red
      inputs
- In this diagram a single ribbon cable is used to bring the signal from
  the Circuit to the Arduino.
  - These outputs are from B11 to B20. These can be replaced with
    individual cables.

### Which Raspberry Pi?

Rather than using a Raspberry Pi model A or B, I decided to use a
Raspberry Pi Zero since the amount of computation required is minimal,
the board is smaller, and the power draw is less. The only disadvantage
is that the Pi has one micro usb port for all of the data. I designed a
case that accommodated the Pi and the USB Hub that I used to connect
ethernet and the Arduino. I set the raspberry pi up with the latest
version of raspbian and 16gb of storage — which should be plenty.

![RaspberryPiZeroW](/Images/raspberryPiZeroW.png) Raspberry Pi Zero W

## CAD Files (optional):

Once the signal was probeable with a multimeter on the contacts of the
protoboard, a 3D printable case was designed for the Arduino and the
perma-protoboard. This case has 3 outputs, 2 ethernet jacks, and a USB A
port for serial communication. No additional hardware is used to secure
the box. After verifying the functionality of the box, I also verified
that the Raspberry Pi was receiving the signal.

The case for Sentry is optional, but highly recommended. Depending on
where sentry is deployed, the case can be an afterthought or a
necessity. The case for sentry was 3D printed on a Creality Ender 3 Pro
in PLA. A custom case made through a different manufacturing process
will work just fine, though modifications may be required for proper
functionality. Otherwise, check your library, office, or an online
service to print these files — often for a low cost. All of the files
were designed in Fusion 360.

Completed Case:

<https://a360.co/2YuOAsf>


If you have all of the same components:

<https://www.thingiverse.com/thing:4457694>

Contains .stl/.iges/.step & the print settings.

![ArduinoProtoCase.png](/Images/ArduinoProtoCase.png)  
![ArduinoProtoCase2.png](/Images/ArduinoProtoCase2.png)  
![ArduinoProtoCase3.png](/Images/ArduinoProtoCase3.png)  
Feel free to modify the models.

##### Usage:

Print 1 of the Top and Bottom Piece, and 2 (or 3) pegs

##### Assembly:

1. Connect the female ethernet jack to the port
2. Put the Protoboard into the top with the 2 pegs.
3. Connect the Arduino to the Protoboard.
4. Put the Arduino into the bottom.
5. Squeeze the sides of the case to slightly deform the plastic and
   allow the latch to grab on
   1. If the “latch” breaks, use a rubber band to secure the box.
6. Connect the wires

![installedBoxWithBrokenClips.jpg](/Images/installedBoxWithBrokenClips.jpg)
Assembled Box, older version had broken pins

###### For the Raspberry Pi Case, I used a solution for my specific USB hub, for most people these cases work well:

- Zero
  - <https://www.thingiverse.com/thing:1167846>
- Zero W
  - <https://www.thingiverse.com/thing:2171313>
- 3b
  - <https://www.thingiverse.com/thing:1572173>
- 4
  - <https://www.thingiverse.com/thing:4154600>
  - <https://www.thingiverse.com/thing:3951002>

## Code and Database:

#### Files and Description:

- activeConfig.py - Command line tool for toggling alarms. Usage python3
  activeConfig --alarm1 off --alarm 2 on
- alarmDB.py - All functions that modify the database
- databaseInitialization.py - Initialize the database using
  defaultvalues.py
- email-sentry.sh - Executes emailConfig.py. Used in Crontab
- emailConfig.py - Reads emails sent to sentry to toggle alarms and
  sends a confirmation email.
- monitor.py - Reads values from serial and adds events to database.
- monitor-sentry.sh - Executes monitor.py. Used in Crontab
- notification.py - Sends a notification with all events after a preset
  delay for active alarms.
- notify-sentry.sh - Executes notification.py. Used in Crontab
- showevents.sh - prints all events in the command line
- Utils.py - Project Wide Functions

#### Arduino Code:

The Arduino reads the 10 most recent voltage values over ~10
milliseconds from the alarm's circuit board and then computes the
average, this average is then computed for all the zones and printed on
the serial port.

##### Sample Voltage Values:

![voltageExample](/Images/voltageExample.png)

#### Database:

The Raspberry Pi listens on the serial port for the voltage, whenever
there is a change in voltage, a python program adds this to the database
in the table “Events”. Each event has a few key parameters, the
startTime, the endTime, and the zone.

A zone is a group of sensors/doors that correspond to a specific area of
your house. If any of the sensors are tripped in the zone, the zone is
triggered and the voltage goes up. Some zones can be 5 windows and a
door, while other zones are a single door. These zones are manually
mapped by the user and hardcoded into the “Zones” table.

Often for alarms, multiple zones need to be monitored, zones can be put
into groups. These have no representation in the wiring and are simply
an easy way to create new alarms with preset groups of zones. Groups are
defined in the “zoneGroups” table. Multiple groups can share zones.
Groups are given names in the “Groups” table

The alarms are defined with 4 parameters, the group, the
activationDelay, the notificationGap, and the minOpenDuration. These
parameters can be shared between alarms — including the group. The
activationDelay specifies the delay from activation when notifications
are ignored. This is mainly to allow people to leave the house after
activating the alarm. The notificationGap is the minimum time before
another notification can be sent. This is usually set high to prevent
notifications from being sent too rapidly. Note: There is a “minimum”
for the notificationGap, this is 15 seconds due to the crontab
configuration. The minOpenDuration is the time which the zone must be
open before triggering an alarm. One use case of setting a high
minOpenDuration is to monitor leaving windows/doors open and then
leaving the house. (THIS FEATURE IS CURRENTLY UNDER DEVELOPMENT)

When the user activates an alarm, it is reflected in the Active Alarms
Table and this is logged in the alarmHistory table for posterity.

![databaseSchema.png](/Images/databaseSchema.png)  
 Database Schema

#### External Interactions:

Sentry can send notifications using email with sms (twilio) as a
fallback. The notification script runs every 15 seconds and checks the
activeAlarms individually and sends an email with all (if any) alarms
having tripped and the timing is after the notificationGap and
activationDelay.

![notification](/Images/notification.png)  
Regularly Scheduled Notification

Sentry can receive emails (with optionally a different email address
than sending), with a preset format to turn off and on alarms. This
allows the user to configure Sentry from outside the house without
tunneling to Sentry or the home network. As a result, this is quite
secure.

![emailConfig.png](/Images/emailConfig.png)  
Confirmation Email after email configuration tool is used

Sentry can be configured through the command line, including changing
the debug level and turning alarms on and off.

## Final Setup:

You must customize, for your environment, defaultvalues.py in order for
everything to work. You will set your alarms, zones, groups, and
credentials here.

Create monitor-sentry.sh and copy to /etc/init.d Edit /etc/rc.local to
include a call to monitor-sentry.sh

Setting PYTHONPATH is essential to ensure packages installed in ~/.local
can be retrieved. Executing as non-root user is essential since
permissions on the python packages installed is quite restrictive.

Make the following entry using crontab -e to install notification.py so
it runs every 15 seconds.

\* * * * * for f in 0 1 2; do /home/pi/python/notify-sentry.sh; sleep
15; done

*/5 * * * * /home/pi/python/email-sentry.sh

Make sure all .sh files are executable.

After setting up the monitoring program in the rc.local to run on boot,
notification program and emailConfig to run every 15 seconds and 5 min
respectively, Sentry finally works, and quite well.

## Planned Features:

- Fix minOpenDuration
  - Modifying notification.py essentially
- Add Scheduling
  - Create a table with alarmId | startTime | endTime
  - Ability to modify table with emailConfig/activeConfig
  - Runs in Crontab every 5 min

