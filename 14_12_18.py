#т.к. питону я только учусь, то я закомментирую всё для себя так, чтобы потом если чего понять что что делает
import requests
#import json
import re
import sqlite3
from bs4 import BeautifulSoup
from time import time
'''
https://regex101.com/

re:
\d = любая цифра
\D = любая НЕ цифра
\w = любой алфавитный символ
\W = любой НЕ алфавитный символ
\s = пробел
\S = НЕ пробел

[0-9] = \d
[1-5]{3} = любые цифры от 1 до 5 3 раза подряд
[A-Z][a-z]+ = 1 заглавный буквенный символ и неограниченое кол-во маленьких после него
...
'''
'''
На всякий случай
headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 6.0; rv:14.0) Gecko/20100101 Firefox/14.0.1',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
	'Accept-Encoding':'gzip, deflate',
	'Connection':'keep-alive',
	'DNT':'1'
}
'''
'''
sql:
conn.execute('SELECT key, p1, p2, p3 FROM table ORDER BY p3')
data0 = conn.fetchall()     = помещение всех результатов
data1 = conn.fetcone()      = помещение 1-ого результата
data2 = conn.fetcone()      = помещение 2-ого результата
data3 = conn.fetcone()      = помещение 3-его результата
data4 = conn.fetcone()      = помещение None при окончании результатов

conn.execute('pragma table_info(table)')  = сведения о колонка таблицы
>>>(<N столбца>, <имя столбца>, <тип данных в столбце>, <что-то>, <и что-то>)

query = 'DROP TABLE IF EXIST'+table
conn.execute(query) = удаление таблицы, если та существует

query = 'DELETE FROM '+table+' WHERE '+id_column+' = "'+record_id'"'
conn.execute(query) = удалить запись из таблицы, где id = определенному значению





'''

links = []
base_url = 'http://spreadreward.com'





#первые 5 def-ов для первой задачи
def get_name(link):
	#Поясню 1 раз на этом, дальше эти 5 get-ов идут по шаблону

	#создание данных для копания в них
	site = requests.get(link).text
	soup = BeautifulSoup(site, features='lxml')
	#Получение нужного tag-а html страницы
	#т.к. страницу строит бот, то у него они все примерно одинаковые
	#потому после нахождения нужного tag-а, если он 1, то ничего не дописываем,
	#если их несколько, то идем через find_all() и ручками определяем нужный из массива
	#tag_X = кусок html кода из целого, в котором находится нужное
	tag_name = soup.find('h1', {'itemprop':'name'})
	#Находим именно то нужное и сразу обрезаем излишки
	#item_X = нужное
	item_name = re.sub(r'(<|>)', '', re.findall(r'>.+<', str(tag_name))[0])#Без str оно не хочет работать
	return  item_name

def get_image_url(link):
	site = requests.get(link).text
	soup = BeautifulSoup(site, features='lxml')
	tag_image_url = soup.find_all('img', {'class':'attachment-shop_catalog wp-post-image'})[-1]
	item_image_url = re.sub(r'(src=\"|\" )', '', re.findall(r'src=\".+\"\s', str(tag_image_url))[0])
	return item_image_url

def get_price(link):
	site = requests.get(link).text
	soup = BeautifulSoup(site, features='lxml')
	tag_price = soup.find('p', {'class':'price'}).find_all('span', {'class':'amount'})[-1]
	item_price = re.sub(r'(<|>руб.)', '', re.findall(r'>.+<', str(tag_price))[0])
	return item_price

def get_category(link):
	site = requests.get(link).text
	soup = BeautifulSoup(site, features='lxml')
	tag_category = soup.find('div', {'class':'product_meta'}).find_all('a')
	#категорий может быть несколько, но по 2 из них групируются в 1. Категории не имеют пересечений
	#потому определю конечную и запомню групировку
	#к сожалению, т.к. мы парсим, то только групировкой руками и можно
	#music = single + albums
	#clothing = hoodies + t-shirts
	#posters
	item_categories=[]
	for cat in tag_category:
		match = re.sub(r'(<|>)', '', re.findall(r'>.+<', str(cat))[0])
		item_categories.append(match)
	#тут мы получили категори_и, осталось определить нужные
	if len(item_categories)>0:
		#вроде бы вот это разделение по длине массива можно убрать, но я не хочу рисковать
		if (str(item_categories[0])=='Music') or (str(item_categories[0])=='Clothing'):
			item_category=str(item_categories[1])
		else:
			item_category=str(item_categories[0])
	else:
		item_category=str(item_categories[0])
	return item_category

def get_description(link):
	site = requests.get(link).text
	soup = BeautifulSoup(site, features='lxml')
	tag_description = soup.find('div', {'itemprop':'description'}).find('p')
	#никаких параметров в нужном тэге нет, потому можно обойтись одним sub-ом
	item_description = re.sub(r'(<p>|</p>)', '', str(tag_description))
	return item_description


#def для 2-ой задачи
def get_links(url):
	#из-за рекурсии надо выкручиваться
	global links, base_url
	#получаем текст ссылки
	site=requests.get(url).text
	soup_main = BeautifulSoup(site, features='lxml')
	#пойду по категориям, чтобы всё найти
	categories = soup_main.find_all('li', {'class':'product-category'})
	#он почему-то не хочет делать массивы, потому сделаю так
	categories_url = re.findall(r'<a.+>', str(categories))
	#теперь магия
	#если категорий нет, то выполнится следующий код
	if len(categories_url)==0:
		#если категорий нет, то выполнится следующий код
		#найдум нужные куски html
		products_of_category = soup_main.find_all('li', {'class':'product'})
		#т.к. у нас массив, то пробежимся по нему
		for product_of_category in products_of_category:
			#там есть 2 tag-а "a", а нам ужен первый. берем из него ссылку
			product_url_of_category=product_of_category.find_all('a')[0].get('href')
			#и канкатанируем с изначальной
			product_url = base_url+product_url_of_category
			links.append(product_url)
	else:
		#если категории есть, то
		#т.к. у нас массив категорий, то пробежимся по ним
		for category in categories_url:
			#делаем новое мыло для поиска в нужной части
			soup=BeautifulSoup(str(category), features='lxml')
			category_url = soup.find('a').get('href')
			#получаем нужную ссылку, канкатанируем и делаем рекурсию
			#рекурсия позволяет войти во _все_ конечные категории
			get_links(url+category_url)
	#на эту функцию у меня ушло 4 часа

def get_categories(curs):
	#запрос на категории
	query = 'SELECT "category" FROM products_table'
	curs.execute(query)
	#обработка запроса и проверка на наличие такой группы уже
	categories=[]
	for category_from_table in curs.fetchall():
		#sql запрос возвращает нам кортеж, потому избавимся от него
		category=category_from_table[0]
		if category in categories:
			pass
		else:
			categories.append(category)
	return categories

def get_prices_of_categories(categories, curs):
	prices_of_category=[]
	prices_of_categories={}
	#пробежимся по каждой категории
	for category_n in range(len(categories)):
		category=categories[category_n]
		#запрос на цены
		query = 'SELECT "price" FROM products_table WHERE "category"="'+category+'"'
		curs.execute(query)
		#т.к. в ответе получим картеж, то избавимя от него
		prices_of_category=[]
		for i in curs.fetchall():
			prices_of_category.append(i[0])
		add={category:prices_of_category}
		prices_of_categories.update(add)
	return prices_of_categories

def get_and_print_avarage_prices(categories, prices_of_categories):
	for category in categories:
		print('Average price for category "'+category+'"')
		pricesof_category=prices_of_categories[category]
		av_price_of_category = sum(pricesof_category)/len(pricesof_category)
		print('%.2f\n'%av_price_of_category)









def main():
	#решил работать с sql тут, т.к. иначе надо будет хранить большое кол-во данных в памяти
	start_time = time()
	#надо её сохранять, иначе он не хочет работать
	conn = sqlite3.connect('./database.db')

	curs=conn.cursor()

	curs.execute('CREATE TABLE IF NOT EXISTS products_table('
		'name TEXT,'#1 имя продукта
		'description TEXT,'#2 описание продукта
		'image_url TEXT,'#3 картинка на продукт
		'price REAL,'#4 цена продукта
		'category TEXT)')#5 категория продукта
	conn.commit()

	get_links(base_url)
	for link in links:
		#получение требуемых данных товара
		name =  get_name(link)
		description = get_description(link)
		image_url = get_image_url(link)
		price = get_price(link)
		category = get_category(link)
		#их сбор для дальнейшего внесения
		product_data = (name, description, image_url, price, category)
		#собственно, внесение и подтверждение
		curs.execute('INSERT INTO products_table VALUES(?, ?, ?, ?, ?)',product_data)
		conn.commit()

	categories = get_categories(curs)
	prices_of_categories = get_prices_of_categories(categories, curs)
	get_and_print_avarage_prices(categories, prices_of_categories)


	curs.close()
	conn.close()

	print('-------------Completed in %.3f seconds-------------' %(time()-start_time))





#если код запущен с консоли, тогда if сработает
#не знаю, зачем мне это, но пускай будет
if __name__=='__main__':
	main()