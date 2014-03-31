"""
Scheduler: Schedule regular events such as alerts and reports

Requires: apscheduler (http://pythonhosted.org/APScheduler/)
"""
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore
import logging
import atexit
import base64
from DataAnalysis.Exceptions.EventError import \
    EventNotFoundError, EventExistsError, EventWontRunError, SchedulerNotFoundError


class EventScheduler():
    """Class to scheduler regular events in a similar manner to cron."""
    __GRACE_PERIOD = 5  # seconds after the designated run time that the job is still allowed to be run
    __mysql_url = 'mysql+pymysql://powermonitor:%s@localhost/powermonitor' \
                  % str(base64.b64decode(bytes('cDB3M3JtMG4xdDBy', 'utf-8')))[2:-1]

    def __init__(self):
        try:
            config = {'apscheduler.daemon': True, 'apscheduler.standalone': False}
            self.__sched = Scheduler(config)
            self.__sched.add_jobstore(SQLAlchemyJobStore(url=self.__mysql_url, tablename='SCHEDULE'), 'default')
            atexit.register(lambda: self.__sched.shutdown(wait=False))  # Stop the scheduler when the program exits
            self.__sched.start()
        except KeyError:
            logging.warning('An error occurred starting the scheduler.')

    def add_cron_event(self, a_func, a_name, a_year=None, a_month=None, a_week=None, a_day=None,
                       a_day_of_week=None, a_hour=None, a_minute=None, a_second=None, a_start_date=None, a_args=None,
                       a_kwargs=None):
        """Add a cron like event to the schedule. Each job must be given a name in case it needs to be removed.
        The following expressions can be used in each field:
        Expression  Field   Description
        *           any     Fire on every value
        */a         any     Fire on every 'a' values, starting from the minimum
        a-b         any     Fire on any value in the 'a-b' range (a must be smaller than b
        a-b/c       any     Fire every 'c' values within the 'a-b' range
        xth y       day     Fire on the x -th occurrence of weekday y within the month
        last x      day     Fire on the last occurrence of weekday 'x' within the month
        last        day     Fire on the last day within the month
        x,y,z       any     Fire on any matching expression; can combine any number of any of the above expressions

        If you want to add **options to the event, use kwargs (keyword arguments dictionary)"""
        if self.__sched is not None:
            event_exists = False
            if self.__find_event(a_name) is not None:
                event_exists = True
            if not event_exists:
                self.__sched.add_cron_job(func=a_func, name=a_name, year=a_year, month=a_month, day=a_day, week=a_week,
                                          day_of_week=a_day_of_week, hour=a_hour, minute=a_minute, second=a_second,
                                          start_date=a_start_date, args=a_args, kwargs=a_kwargs,
                                          misfire_grace_time=self.__GRACE_PERIOD)
                logging.info('New cron event added')
            else:
                raise EventExistsError('A job with name %s already exists' % a_name)
                logging.warning('add_cron_event: Event already exists')
        else:
            raise SchedulerNotFoundError('add_cron_event: Scheduler does not exist. It may have not started.')

    def __find_event(self, a_event_name):
        if self.__sched is not None:
            events = self.__sched.get_jobs()
            for event in events:
                if event.name is a_event_name:
                    return event
                else:
                    return None
        else:
            raise SchedulerNotFoundError('Scheduler does not exist. It may have not started.')
            logging.warning('__find_event: Scheduler does not exist. It may have not started.')

    def add_onceoff_event(self, a_func, a_name, a_date, a_args=None):
        """Add a once off event to the schedule. The job is executed once at the specified date and time.
        Date/time format: YYYY-MM-DD HH:MM:SS"""
        if self.__sched is not None:
            try:
                if a_args is None:
                    self.__sched.add_date_job(func=a_func, name=a_name, date=a_date, misfire_grace_time=self.__GRACE_PERIOD)
                else:
                    self.__sched.add_date_job(func=a_func, name=a_name, date=a_date, arge=a_args,
                                              misfire_grace_time=self.__GRACE_PERIOD)
            except ValueError:
                raise EventWontRunError('The event will not run: Event time has expired.')
            logging.info('New once off event added')
        else:
            raise SchedulerNotFoundError('Scheduler does not exist. It may have not started.')
            logging.warning('add_onceoff_event: Scheduler does not exist. It may have not started.')

    def remove_event(self, event_name):
        """Remove the event 'event_name' from the schedule."""
        if self.__sched is not None:
            removed = False
            event = self.__find_event(event_name)
            if event is not None:
                self.__sched.unschedule_job(event)
                removed = True
            if not removed:
                raise EventNotFoundError('Event not found for removal: %s' % event_name)
                logging.warning('remove_event: Event not found for removal.')
        else:
            raise SchedulerNotFoundError('remove_event: Scheduler does not exist. It may have not started.')

    def get_events(self):
        """Get the list of events currently in the job store."""
        if self.__sched is not None:
            return self.__sched.get_jobs()
        else:
            raise SchedulerNotFoundError('get_events: Scheduler does not exist. It may have not started.')

    def get_scheduler(self):
        """Returns the Scheduler object. Rather add functionality to this class than call this method."""
        if self.__sched is not None:
            return self.__sched
        else:
            raise SchedulerNotFoundError('get_scheduler: Scheduler does not exist. It may have not started.')