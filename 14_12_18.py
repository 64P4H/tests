#т.к. питону я только учусь, то я закомментирую всё для себя так, чтобы потом если чего понять что что делает
import requests
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


#первые 6 def-ов для первой задачи
def get_name(soup):
	#Поясню 1 раз на этом, следующие 5 get-ов идут по шаблону

	#Получение нужного tag-а html страницы
	#т.к. страницу строит бот, то у него они все примерно одинаковые
	#потому после нахождения нужного tag-а, если он 1, то ничего не дописываем,
	#если их несколько, то идем через find_all() и ручками определяем нужный из массива
	#tag_X = кусок html кода из целого, в котором находится нужное
	tag_name = soup.find('h1', {'itemprop':'name'})
	#Находим именно то нужное и возвращаем обратно
	#item_X = нужное
	item_name = tag_name.string
	return  item_name

def get_image_url(soup):
	#там в коде сперва идут 3 относящиеся товара, и четвертым идет нужный товар, но -1 то же идёт
	tag_image_url = soup.find_all('img', {'class':'attachment-shop_catalog wp-post-image'})[-1]
	item_image_url = tag_image_url.get('src')
	return item_image_url

def get_price(soup):
	#цена может быть со скидкой, старя указывается первой, потому нам нужна вторая
	#но на всякий случай поставим -1
	tag_price = soup.find('p', {'class':'price'}).find_all('span', {'class':'amount'})[-1]
	#надо обрезать, т.к. есть "руб."
	#т.к. 2 арг = ДО, то нам надо сканкатаниорвать с последнийм символом
	item_price = tag_price.string[4:-1]+tag_price.string[-1]
	return item_price

def get_category(soup):
	#категорий может быть несколько, но по 2 из них групируются в 1. Категории не имеют пересечений
	#потому определю конечную и запомню групировку
	#к сожалению, т.к. мы парсим, то только групировкой руками и можно
	#music = single + albums
	#clothing = hoodies + t-shirts
	#posters не делится
	#получаем 1 или 2 тега
	tags_with_categories = soup.find('div', {'class':'product_meta'}).find_all('a')
	#пробегаемся по ним
	for tag_category in tags_with_categories:
		item_category=tag_category.string
		#выбираем нужное и возвращаем
		if item_category!='Music' and item_category!='Clothing':
			return item_category

def get_description(soup):
	tag_description = soup.find('div', {'itemprop':'description'}).find('p')
	item_description = tag_description.string
	return item_description

def get_product_data(link):
	#создание данных для копания в них
	site = requests.get(link).text
	soup = BeautifulSoup(site, features='lxml')
	#получение имени
	name = get_name(soup)
	#получение url адреса картинки
	image_url = get_image_url(soup)
	#получение цены
	price = get_price(soup)
	#получение категории
	category = get_category(soup)
	#получение описания
	description = get_description(soup)
	#передача данных о товарах !!!в правильном порядке!!!!
	return name, description, image_url, price, category



#def для 2-ой задачи
def get_links(url):
	#из-за рекурсии надо выкручиваться
	global links, base_url
	#получаем текст ссылки
	site=requests.get(url).text
	soup = BeautifulSoup(site, features='lxml')
	#пойду по категориям, чтобы найти все товары
	#теперь магия
	#поиск категорий
	li_s_with_urls = soup.find_all('li', {'class':'product-category'})
	if len(li_s_with_urls)==0:
		#если категорий нет, то выполнится следующий код
		#найдём нужные куски html
		products_of_category = soup.find_all('li', {'class':'product'})
		#т.к. у нас массив, то пробежимся по нему
		for product_of_category in products_of_category:
			#там есть 2 tag-а "a", а нам ужен первый. берем из него ссылку
			product_url_of_category=product_of_category.find('a').get('href')
			#и канкатанируем с изначальной
			product_url = base_url+product_url_of_category
			links.append(product_url)
	else:
		#если категории есть, то
		#т.к. у нас массив категорий, то пробежимся по ним
		for li_with_url in li_s_with_urls:
			category_url = li_with_url.find('a').get('href')
			#получаем нужную ссылку, канкатанируем и делаем рекурсию
			#рекурсия позволяет войти во _все_ конечные категории
			get_links(url+category_url)

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
	#надо сохранять таблицу, иначе он не хочет работать
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
		#получение требуемых данных товара и их сбор для дальнейшего внесения
		product_data = (get_product_data(link))
		#собственно, внесение и подтверждение
		
		curs.execute('INSERT INTO products_table VALUES(?, ?, ?, ?, ?)',product_data)
		conn.commit()
	#всё для четвертой задачи
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