#!/usr/bin/env python2
# This script should be run on system startup. TODO: Create systemd startup service

import logging
import jobtriggers as jt    # for bound methods
from Events.EventScheduler import EventScheduler as ES
from DataAnalysis.Exceptions.EventError import EventExistsError
import time

# Add any jobs that you to run at specific intervals or on specific dates
# This script will check if the event is in the jobstore, and if it doesn't exist, it will create and start it

# The format is {name of job, method.in.powermonitor, event type, {schedule: values}}

startup_list = [
    {'name': 'PowerAlertScraper.renew_tags',
     'method': jt.power_alert_scraper__renew_tags,
     'type': 'cron',
     'schedule': {
         'year': None, 'month': None, 'week': None, 'day': None, 'day_of_week': None, 'hour': None, 'minute': '*/30',
         'second': None}}
]

# call the instance of the scheduler
scheduler = ES()
jobs = scheduler.get_job_names()

for event in startup_list:
    if event['name'] not in jobs:
        # if the event type is cron, then we must add it to the jobstore appropriately
        if event['type'] == 'cron':
            try:
                scheduler.add_cron_event(
                    event['method'],
                    name=event['name'],
                    year=event['schedule']['year'],
                    month=event['schedule']['month'],
                    week=event['schedule']['week'],
                    day=event['schedule']['day'],
                    day_of_week=event['schedule']['day_of_week'],
                    hour=event['schedule']['hour'],
                    minute=event['schedule']['minute'],
                    second=event['schedule']['second']
                )
            except EventExistsError:
                # If the event exists, we need to know about it, but don't just crash...that would be silly
                logging.warning('An event with name %s exists, try renaming the event.' % event['name'])
        # otherwise the job is a onceoff
        elif event['type'] == 'onceoff':
            try:
                scheduler.add_onceoff_event(
                    event['method'],
                    name=event['name'],
                    date=event['date']
                )
            except EventExistsError:
                # again, show a message if an event with the same name exists
                logging.warning('An event with name %s exists, try renaming the event.' % event['name'])
        else:
            # otherwise some silly noob gave the incorrect event type
            logging.warning('Invalid event type: %s' % event['type'])
            raise ValueError('Invalid event type: %s' % event['type'])

# and this will ensure that the scheduler continues to run until the Pi dies.
while True:
    time.sleep(99999)