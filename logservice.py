#!/usr/bin/env python
from __future__ import division
from GPIOInterface.powermonitor import PowerMonitor
from Database.DBConnect import DbConnection
from time import sleep

pw=PowerMonitor()
database=DbConnection.instance()


database.execute_non_query("INSERT INTO powermonitorweb_readings(reading) VALUES -1")

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
        #Save to the database every minute, with readings 10 times a second
        while len(readings)<600:
            readings.append(pw.read_watts())
            sleep(100)
        average=sum(readings)/len(readings)
        database.execute_non_query("INSERT INTO powermonitorweb_readings(reading) VALUES %s",(average,))
    #Something killed the sensor
    #Not sure what to do with this
    #depends if it's transient or chronic