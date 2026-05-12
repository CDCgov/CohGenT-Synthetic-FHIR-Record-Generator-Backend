from datetime import date, datetime, timedelta
from random import randrange, randint
from dateutil.relativedelta import relativedelta
from api.models.value_types import ValueTimeRangeAsDays


def generate_age_at_event_date(min: int, max: int):
    age_at_diagnosis = randrange(min, max)
    return age_at_diagnosis

def calculate_birth_date(event_date: date, age_at_diagnosis: int):
    birth_date: date = event_date - relativedelta(years=age_at_diagnosis)
    return birth_date

def generate_event_datetime(start: date, end: date) -> date:
    '''
    This function only returns dates. If time is required, should be handled in parsing function call.
    '''
    event_date = random_date(start, end)
    return event_date

def random_date(start: date, end: date) -> date:
    '''
    Randomly generate a date between two other dates.
    '''
    between: timedelta = end - start
    days: int = between.days
    random_day: int = randrange(days)
    return start + timedelta(random_day)

def append_days(event_date: datetime | date, range: ValueTimeRangeAsDays) -> datetime | date:
    days = randint(range.start, range.end)
    appended_date = event_date + timedelta(days)
    return appended_date