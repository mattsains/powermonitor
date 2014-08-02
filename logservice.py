#!/usr/bin/env python2
from __future__ import division
from GPIOInterface.powermonitor import PowerMonitor
from Database.DBConnect import DbConnection
import time

pw=PowerMonitor()
database=DbConnection()

database.execute_non_query("IF (SELECT count(*) FROM powermonitorweb_readings) > 0 THEN \
                                INSERT INTO powermonitorweb_readings(time, reading) \ 
                                VALUES ((SELECT MAX(time) FROM powermonitorweb_readings),0)")
database.execute_non_query("INSERT INTO powermonitorweb_readings(reading) VALUES (0)")

while True:
    response=pw.handshake()
    while (response!=False):
        if response["NO_VOLTAGE"] :
            #Let the web interface know about the lack of voltage signal
            database.execute_non_query("UPDATE powermonitor_configuration SET value=1 WHERE field='no_voltage'")
        if response["OVER_CURRENT"]:
            #Let the web interface know about the damaging current condition
            database.execute_non_query("UPDATE powermonitor_configuration SET value=1 WHERE field='over_current'")
        
        readings=[]
        #Save to the database every minute
        stop_time=time.time()+60
        while time.time() < stop_time:
            readings.append(pw.read_watts())
        average=sum(readings)/len(readings)
        if (average<0):
            average=0 #clamp invalid values
        database.execute_non_query("INSERT INTO powermonitorweb_readings(reading) VALUES (%s)",(average,))
    #Something killed the sensor
    #Not sure what to do with this
    #depends if it's transient or chronic
