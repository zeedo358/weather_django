from datetime import date, timedelta
from .info_manager import execute


def run(city):
    dates = [(date.today() + timedelta(days = i)).strftime('%Y.%m.%d') for i in range(7)]
    result = [execute(city,date_) for date_ in dates]
    return result
