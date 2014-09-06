#!/usr/bin/python2
import socket
import smtplib
from email.mime.text import MIMEText

def sendmail():
    msg = MIMEText(socket.gethostbyname(socket.gethostname()))
    msg['Subject'] = 'Raspberry Pi IP Address'
    msg['From'] = 'powermonitor.ecoberry@gmail.com'
    msg['To'] = 'powermonitor.ecoberry@gmail.com'

    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login('powermonitor.ecoberry@gmail.com', 'password')  # TODO: enter actual password before we deploy!!!
        # Send an email to yourself...? Why not?
        server.sendmail('powermonitor.ecoberry@gmail.com', 'powermonitor.ecoberry@gmail.com', msg.as_string())
        server.close()
    except Exception as e:
        """no point in doing anything because no one will see it"""

sendmail()