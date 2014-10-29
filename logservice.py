#!/usr/bin/env python2
from __future__ import division
from GPIOInterface.powermonitor import PowerMonitor
from Database.DBConnect import DbConnection
from datetime import datetime
from dateutil.relativedelta import relativedelta

pw=PowerMonitor()
database=DbConnection()
#
# database.execute_non_query("IF (SELECT count(*) FROM powermonitorweb_readings) > 0 THEN \
#                                 INSERT INTO powermonitorweb_readings(time, reading) \
#                                 VALUES (DATE_ADD((SELECT MAX(time) FROM powermonitorweb_readings),SECOND,1),0)")
# database.execute_non_query("INSERT INTO powermonitorweb_readings(reading) VALUES (0)")

rowcount = database.execute_query("select count(*) from powermonitorweb_readings;")
if list(rowcount)[0][0] > 0:
    print("Recovering from power failure")
    while True:
        database.execute_query('INSERT INTO powermonitorweb_readings(time, reading) VALUES (DATE_ADD((SELECT MAX(time) \
                                FROM powermonitorweb_readings as new_time), INTERVAL 1 MINUTE),0);')
        last_time=database.execute_query('select max(time) from powermonitorweb_readings;')
        if list(last_time)[0][0] >= datetime.utcnow():
            break;

print("starting to collect data.")
while True:
    response=pw.handshake()
    while (response!=False):
        if response["NO_VOLTAGE"]:
            #Let the web interface know about the lack of voltage signal
            database.execute_non_query("UPDATE powermonitorweb_configuration SET value=1 WHERE field='no_voltage'")
        if response["OVER_CURRENT"]:
            #Let the web interface know about the damaging current condition
            database.execute_non_query("UPDATE powermonitorweb_configuration SET value=1 WHERE field='over_current'")
        
        sum=0
        count=0
        #Save to the database every minute
        stop_time=datetime.now()+relativedelta(seconds=60)
        print "Collecting readings..."
        while datetime.now() < stop_time:
            sum+=pw.read_watts()
            count+=1
        print "averaging..."
        average=sum/count
        if (average<0):
            average=0 #clamp invalid values
        print "updating db"
        print database.execute_non_query("INSERT INTO powermonitorweb_readings(reading) VALUES (%s)",(average,))
    #Something killed the sensor
    #Not sure what to do with this
    #depends if it's transient or chronic
