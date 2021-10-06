from datetime import date
from . import configure

class DateManager:
	"""docstring for DataManager"""
	def __init__(self, usr_date):
		self.date_ = date(*map(int,usr_date.split('.')))
		self._days = configure.DAYS
		self._months = configure.MONTHS
	def get_day(self):
		#returns name of day of date was given
		return self._days[self.date_.weekday()]
	def get_month(self):
		#returns name of month of date was given
		return self._months[self.date_.month - 1]