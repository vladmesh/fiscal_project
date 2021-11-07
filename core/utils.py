import datetime

from dateutil import tz


def change_timezone(old_date, timezone_from, timezone_to) -> datetime.datetime:
    from_zone = tz.gettz(timezone_from)
    to_zone = tz.gettz(timezone_to)
    tmp = old_date.replace(tzinfo=from_zone)
    new_date = tmp.astimezone(to_zone)
    return new_date


def strip(arg):
    if isinstance(arg, str):
        arg = arg.strip()
    return arg
