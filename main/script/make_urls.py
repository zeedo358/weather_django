from . import configure

class MakeUrls():
	"""Class makes the url adress for making a request"""
	def __init__(self, place,date):
		self.place = place.replace(' ','-')
		self.date = date
		self._transcription_leters = configure.localization
	
	def make_urls(self):
		google_url = configure.URL_GOOGLE.format(self.place,self.date.date_.strftime("%d"),self.date.date_.strftime("%m"))
		sinoptik_url = configure.URL_SINOPTIK.format(self.place,str(self.date.date_))
		pogoda33_url = configure.URL_POGODA33.format(self.place)
		meteotrend_url = configure.URL_METEOTREND.format(self._localize_place())
		return {'google':google_url,'sinoptik':sinoptik_url,'pogoda33':pogoda33_url,'meteotrend':meteotrend_url}

	def _localize_place(self):
		localized_place = self.place
		for key,value in self._transcription_leters.items():
			localized_place = localized_place.replace(key,value)
		return localized_place


