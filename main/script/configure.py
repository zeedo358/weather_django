URL_GOOGLE = 'https://www.google.com/search?q=погода+{}+{}.{}'
URL_SINOPTIK = 'https://ua.sinoptik.ua/погода-{}/{}'
URL_POGODA33 = 'https://pogoda33.ua/погода-{}/тиждень'
URL_METEOTREND = 'https://ua.meteotrend.com/forecast/ua/{}/'

DAYS = ('понеділок','вівторок','середа','четвер','пʼятниця','субота','неділя')
MONTHS = ('січня','лютого','березня','квітня','травня','червня','липня','серпня','вересня','жовтня','листопада','грудня')
HEADERS = {
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
	'accept':'*/*'
}

localization = {'й':'i','ц':'ts','у':'u','к':'k','е':'e','н':'n','г':'h',
'ш':'sh','щ':'sch','з':'z','х':'kh','ї':'i','ф':'f',
'і':'i','в':'v','а':'a','п':'p','р':'r','о':'o','л':'l','д':'d','ж':'zh','є':'ie',
'ґ':'g','я':'ia','ч':'ch','с':'s','м':'m','и':'y','т':'t','ь':'','б':'b','ю':'iu'
}