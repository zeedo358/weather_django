import asyncio
import pickle
import time

from .make_urls import MakeUrls
from .date_manager import DateManager
from .info_parser import Parser


class Manager:
	"""Class which manages all information,making average data from all data was given"""
	def __init__(self,place,usr_date):
		self.place = place
		self.date_ = DateManager(usr_date)

	def _get_info(self):
		urls = MakeUrls(self.place,self.date_).make_urls()
		info_getter = Parser(urls,self.date_)
		info = asyncio.run(info_getter.get_info())
		return info

	def manage_info(self):
		data = self._get_info()
		while None in data:
			data.remove(None)
		managed_information = {'kind_of_weather':'','avg_temp':0,'avg_fallings':0,'temp':[0,0,0,0],'fallings':[0,0,0,0]}
		# managing data of avg fallings and avg temperature
		for info in data:
			managed_information['avg_temp'] += info['avg_temp']
			managed_information['avg_fallings'] += info['avg_fallings']
		else:
			managed_information['avg_temp'] = round(managed_information['avg_temp'] / len(data),1)
			managed_information['avg_fallings'] = round(managed_information['avg_fallings'] /len(data),1)

		# managing data of fallings and temperature for halfs of day
		len_temp = 0
		len_fallings = 0
		for i in range(len(managed_information['temp'])):
			for half_data_day in data:
				value_temp = half_data_day['temp'][i]
				value_falling = half_data_day['fallings'][i]
				if value_temp != None:
					managed_information['temp'][i] += value_temp
					len_temp += 1
				if value_falling != None:
					managed_information['fallings'][i] += value_falling
					len_fallings += 1
			else:
				managed_information['temp'][i] = round(managed_information['temp'][i] / len_temp,1)
				managed_information['fallings'][i] = round(managed_information['fallings'][i] / len_fallings,1)
				len_temp = 0
				len_fallings = 0

		if 8 < managed_information['avg_fallings'] <= 15 and managed_information['avg_temp'] <= 0:
			managed_information['kind_of_weather'] = 'Невеликий сніг'
		elif managed_information['avg_fallings'] > 15 and managed_information['avg_temp'] <= 0:
			managed_information['kind_of_weather'] = 'Сніг'
		elif 8 < managed_information['avg_fallings'] <= 15 and managed_information['avg_temp'] > 0:
			managed_information['kind_of_weather'] = 'Невеликий дощ'
		elif  15 < managed_information['avg_fallings'] <= 50 and managed_information['avg_temp'] > 0:
			managed_information['kind_of_weather'] = 'Дощ'
		elif  50 < managed_information['avg_fallings'] and managed_information['avg_temp'] > 0:
			managed_information['kind_of_weather'] = 'Зливи'
		elif  2.5 < managed_information['avg_fallings'] <= 8:
			managed_information['kind_of_weather'] = 'Похмуро'
		elif 0.5 <= managed_information['avg_fallings'] <= 2.5:
			managed_information['kind_of_weather'] = 'Хмарно'
		elif managed_information['avg_fallings'] < 0.5:
			managed_information['kind_of_weather'] = 'Ясно'

		return managed_information


def _save_data(data):
	with open('data.pickle','wb') as file:
		pickle.dump(data,file)

def _load_data():
	try:
		with open('data.pickle','rb') as file:
			return pickle.load(file)
	except FileNotFoundError:
		return {}



def execute(city,date):
	data = _load_data()
	last_time_updated = data.get(city) # 0 - last time of update, 1 - data
	if last_time_updated == None or last_time_updated.get(date) == None or time.time() - last_time_updated[date][0] > 7200:
		request = Manager(city,date)
		result_of_request = request.manage_info()
		if data.get(city) != None:
			data[request.place].update({date:[time.time(),result_of_request]})
		else:
			data[request.place] = {date:[time.time(),result_of_request]}
		_save_data(data)
	return data[city][date][1]



