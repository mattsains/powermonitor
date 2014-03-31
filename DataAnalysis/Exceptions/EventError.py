class EventNotFoundError(Exception):
    pass


class EventWontRunError(Exception):
    pass


class EventExistsError(Exception):
    pass


class SchedulerNotFoundError(Exception):
    pass