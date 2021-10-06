import asyncio
import re
import datetime

import aiohttp
from aiohttp.web import HTTPTooManyRequests
from bs4 import BeautifulSoup

from . import configure

class TownError(Exception):
	pass

class Parser:
	"""Main class of parsers, which includes 2 functions for getting html code of urls"""
	def __init__(self,urls,date):
		self.urls = dict(urls)
		self.date = date
		self.registered_methods = []

	async def _make_request(self,url):
		# making a request to a web site
		async with aiohttp.ClientSession() as session:
			async with session.get(url,headers = configure.HEADERS) as response:
				if response.status == 200:
					return await response.text()
				elif response.status == 429:
					raise HTTPTooManyRequests
				elif response.status == 404:
					raise TownError
				else:
					return

	async def _get_soup(self,url):
		# returns BeatutifulSoup object for working with it
		i = 0
		while i < 5:
			try:
				result = await self._make_request(url)
			except HTTPTooManyRequests:
				i += 1
				await asyncio.sleep(0.2)
			else:
				break
		else:
			raise HTTPTooManyRequests

		return BeautifulSoup(result,'html.parser')

	async def get_info(self):
		#calling all parsers
		info = await asyncio.gather(self.sinoptik_parser(),
		self.google_parser(),
		self.meteotrend_parser(),
		self.pogoda33_parser())

		return info

	async def google_parser(self):
		# taking information from the google website
		separator = r'\d+'
		information = {'kind_of_weather':'','avg_temp':0,'avg_fallings':0,'temp':[None,None,None,None],'fallings':[None,None,None,None]}
		#get fallings
		soup = await self._get_soup(self.urls['google'])
		items = soup.find_all('div',class_ = 'XwOqJe')
		fallings = []

		if not items:
			return None

		for i,elem in enumerate(items):
			# taking 24 hours for day we need
			if i < (24 - datetime.datetime.now().hour) + ((self.date.date_ - self.date.date_.today()).days * 24) and i >= (23 - datetime.datetime.now().hour) + (((self.date.date_ - self.date.date_.today()).days -1) * 24): # 24 hours
				data = elem.get('aria-label')
				if self.date.get_day() in data:
					fallings.append(int(re.search(separator,data).group(0)))

		#average fallings for time:
		if self.date.date_ != self.date.date_.today():
			fallings_for_time = [sum(fallings[0:7])/6,sum(fallings[7:13])/6,sum(fallings[13:19])/6,sum(fallings[19:24])/6] # 6 hour half of day
			information['fallings'] = fallings_for_time

		# average fallings
		try:
			avg = sum(fallings) / len(fallings)
		except ZeroDivisionError:
			raise TownError
		information['avg_fallings'] = avg

		#average temperature
		temperature = soup.find('span',id = 'wob_tm').text
		information['avg_temp'] = float(temperature)

		#kind of weather
		kind = soup.find('span',id = 'wob_dc').text
		information['kind_of_weather'] = kind

		return information

	async def meteotrend_parser(self):
		# taking information from the meteotrend website
		information = {'kind_of_weather':'','avg_temp':0,'avg_fallings':0,'temp':[None,None,None,None],'fallings':[None,None,None,None]}
		times = ['ніч','ранок','день','вечір']
		fell_rain = 0
		searched_day = '{}, {} {} {}'.format(self.date.get_day(),self.date.date_.day,self.date.get_month(),self.date.date_.year)


		soup = await self._get_soup(self.urls['meteotrend'])
		blocks = soup.find_all('div',class_ = 'box')

		for block in blocks:
			name = block.find('h5').text
			# checking is this day we're searching
			if repr(name.replace('\'','ʼ').strip()) != repr(searched_day):
				continue
			info_for_blocks = block.findAll('div',class_ = 'm7')
			for info in info_for_blocks:
				key = times.index(info.find('td',class_='dtm').find('b').text)
				fallings = [item.text for item in info.find('div',class_ = 'wtpo').find_all('b') if 'мм' in item.text and len(item.text) <= 6]
				# converting fell rain into percents of fallings
				if fallings:
					fell_rain = float(fallings[0][:-2].replace(',','.')) * 30
					if fell_rain > 100: fell_rain = 100
					information['fallings'][key] = fell_rain
				else:
					information['fallings'][key] = 0

				data = [item.text for item in info.find('td',class_ = 't0').find_all('b')]
				if len(data) == 3:
					avg_temp = (float(data[0])+float(data[1][:3]))/2
					mini_desc = data[2]
				else:
					avg_temp = (float(data[0][:3])+float(data[0][:3]))/2
					mini_desc = data[1]
				information['temp'][key] = avg_temp
				#taking kind of weather from middle time of day 
				if key == 2:
					information['kind_of_weather'] = mini_desc
		# average temperature, fallings
		len_temp = 0
		len_fallings = 0
		for elem,elem2 in zip(information['temp'],information['fallings']):
			if elem != None:
				information['avg_temp'] += elem
				len_temp += 1
			if elem2 != None:
				information['avg_fallings'] += elem2
				len_fallings += 1
		try:
			information['avg_temp'] /= len_temp
			information['avg_fallings'] /= len_fallings
		except ZeroDivisionError:
			pass
		
		return information

	async def pogoda33_parser(self):
		# taking information from the pogoda33 website
		information = {'kind_of_weather':'','avg_temp':0,'avg_fallings':0,'temp':[None,None,None,None],'fallings':[None,None,None,None]}

		soup = await self._get_soup(self.urls['pogoda33'])
		# time starts with 00:00 step = 3 hours
		# parsing all information for all days in week
		kind_of_weather = [item.text for item in soup.find_all('div',class_ = 'col-3 col-md-2 sky-icon my-auto')]
		if not kind_of_weather:
			return None
		temperature  = [item.text for item in soup.find_all('span',class_ = 'forecast-temp')]
		fallings = [item.text for item in soup.find_all('div',class_ = 'col-md-1 w-middle d-none d-md-block')[::2]]

		division_in_days = ((self.date.date_ - self.date.date_.today()).days) * 8 # 8 hours at half a day
		# temp and avg_temp
		information['temp'] = [sum(float(elem[:-1]) for elem in temperature[division_in_days:division_in_days + 3])/3,sum(float(elem[:-1]) for elem in temperature[division_in_days+3:division_in_days + 5])/2,sum(float(elem[:-1]) for elem in temperature[division_in_days+5:division_in_days + 7])/2,sum(float(elem[:-1]) for elem in temperature[division_in_days+7:division_in_days + 8])]
		information['avg_temp'] = sum(information['temp']) / len(information['temp'])
		#kind of weather
		information['kind_of_weather'] = kind_of_weather[int((division_in_days * 2 + 9) / 2)]
		# converting fallings into percents
		for i,elem in enumerate(fallings):
			fallings[i] = float(elem[:-2].replace(',','.').replace(' ','')) * 30
			if fallings[i] > 100: fallings[i] = 100
		#falling and avg_fallings
		information['fallings'] = [float(sum(fallings[division_in_days:division_in_days + 3])/3),float(sum(fallings[division_in_days+3:division_in_days + 5])/2),float(sum(fallings[division_in_days+5:division_in_days + 7])/2),float(sum(fallings[division_in_days+7:division_in_days + 8]))]
		information['avg_fallings'] = sum(information['fallings']) / len(information['fallings'])

		return information

	async def sinoptik_parser(self):
		# taking information from the sinoptik website
		information = {'kind_of_weather':'','avg_temp':0,'avg_fallings':0,'temp':[0,0,0,0],'fallings':[0,0,0,0]}
		#getting all information for the day
		soup = await self._get_soup(self.urls['sinoptik'])
		items = soup.find_all('tr',class_ = None)[2].findAll('td')
		fallings = [item.text for item in items]
		items = soup.find('tr',class_ = 'temperature').findAll('td')
		temperature = [item.text for item in items]

		#fallings and temperature
		if len(fallings) == 4:
			information['fallings'] = list(map(float,fallings))
			information['temp'] = list(map(float,(temp[:-1] for temp in temperature)))
		else:
			i = 0
			for j in range(len(fallings)):
				if j % 2 == 0 and j != 0:
					information['fallings'][i] /= 2
					information['temp'][i] /= 2
					i += 1
				if fallings[j] == '-':
					if j + 1 < len(fallings) and fallings[j + 1] != '-':
						information['fallings'][i] += float(fallings[j + 1]) * 0.7
					elif fallings[j - 1] != '-' and j != 0:
						information['fallings'][i] += float(fallings[j - 1]) * 0.7
					else:
						information['fallings'][i] += 0
				else:
					information['fallings'][i] += float(fallings[j])
				information['temp'][i] += float(temperature[j][:-1])
			else:
				information['fallings'][-1] /= 2
				information['temp'][-1] /= 2

		#avg_fallings and avg_temp
		information['avg_fallings'] = sum(information['fallings'])/len(information['fallings'])
		information['avg_temp'] = sum(information['temp'])/len(information['temp'])
		
		return information

		