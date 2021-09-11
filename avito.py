#version 1.8

#Spone 22.02.20
#1.1 Добавлен ввод url
#1.2 Добавлено имя файла.csv
#1.3 Исправлена ошибка с отображением цены товара
#1.4 Вывод сообщения о создании файла
#1.5 Проверка на корректность ссылки (параметры) и что является сайтом avito
#1.6 Полностью переписана структура параметров, добавлен радиус и геолокация
#1.7 Убрана завязка на количество страниц, теперь если только одна страница, то берётся только с неё
#1.8 Сделана замена неизвестных символов юникода на (?), добавлены новые атрибуты

#Необходимо исправить кол-во

import requests
from bs4 import BeautifulSoup
import csv
import re
from unidecode import unidecode
from urllib.request import urlopen

titles = {'title'       : 'Наименование',
          'price'       : 'Цена',
          'description' : 'Описание',
          'url'         : 'URL адрес'}

def getHtml(url):
    r = requests.get(url)
    return r.text

def getTotalPages(html):
    soup = BeautifulSoup(html, 'lxml')
    
    try:
        pages = soup.find_all('span', class_='pagination-item-JJq_j')[-2].get('data-marker')
        p = pages.split('(')[1].split(')')[0]
    except:
        p = 1

    return int(p)

def deleteSymbol(str):
    return re.sub(r'[^0-9.]+', r'', str)

def getPageData(html):
    soup = BeautifulSoup(html, 'lxml')

    try:    
        name_file = soup.find('a', {'class':'rubricator-list-item-link_current-fnAHj'})['title']
    except Exception as e:
        name_file = 'None'

    ads = soup.find_all('div', class_='iva-item-content-UnQQ4')
    writeCsv(titles, name_file) ##write title
                         
    for ad in ads:
        #title,price, description, url
        try:
            title = ad.find('h3', class_='title-root-j7cja').text.strip()
        except:
            title = ''
        try:
            pr = ad.find('span', class_='price-text-E1Y7h').text.strip()
            price = deleteSymbol(pr) + 'р.'
        except:
            price = ''    
        try:
            url = 'https://www.avito.ru/' + ad.find('a', {'class':'link-link-MbQDP'})['href']
        except:
            url = '' 
        try:
            description = ad.find('div', class_='iva-item-description-S2pXQ').text.strip()
        except:
            description = ''           

        data = {'title':title,
                'price':price,
                'url':url,
                'description':description}

        writeCsv(data, name_file)

    return name_file
    #return ads

def writeCsv(data, name_file = 'avito'):
    #newline = '' (3 параметр, убрать разделение между строками)
    with open(str(name_file) +'.csv','a', encoding="cp1251", newline='', errors='replace') as f:
        writer = csv.writer(f, delimiter=';')
      
        writer.writerow((data['title'],
                         data['price'],
                         data['description'],
                         data['url']
                         ))

def pasteTotal(url, name_file = 'avito'):
    text = getHtml(url)
    soup = BeautifulSoup(text, 'lxml') 

    try:
        total = soup.find('span', class_='page-title-count-wQ7pG').text
    except:
        total = 0
    try:        
        name_razdel = soup.find('h1', class_='page-title-inline-zBPFx').text.strip()
    except:
        name_razdel = ''    

    data = {'total': total,
            'name_razdel':name_razdel
           }

    write_shapka_csv(data,name_file)       

def write_shapka_csv(data, name_file = 'avito'):
    #newline = '' (3 параметр, убрать разделение между строками)
    with open(str(name_file) +'.csv','a', encoding="cp1251", newline='') as f:
        writer = csv.writer(f, delimiter=';')
      

        writer.writerow((data['name_razdel'],
                         data['total']
                         ))

def main(path):
    
    if(path.find('avito.ru') == -1):
        print('Вы вставили ссылку не с сайта Avito.ru!')
        return
    if(path.find('?') == -1):
        print('Ваша URL ссылка не имеет параметров! Парсинг невозможен!')
        return

    base_url = path.split('?')[0] + '?' #link before parametrs
    base_params = path.split('?')[1] #attributes
    
    atributes = ''   
    if(base_params.find('cd=') != -1):
        atributes = atributes + 'cd' + base_params.split('cd')[1].split('&')[0] + '&'   

    if(base_params.find('radius=') != -1):    
        atributes = atributes + 'radius' + base_params.split('radius')[1].split('&')[0] + '&'
    
    if(base_params.find('geoCoords=') != -1):   
        atributes = atributes + 'geoCoords' + base_params.split('geoCoords')[1].split('&')[0] + '&'

    if(base_params.find('pmax=') != -1):   
        atributes = atributes + 'pmax' + base_params.split('pmax')[1].split('&')[0] + '&'

    if(base_params.find('pmin=') != -1):   
        atributes = atributes + 'pmin' + base_params.split('pmin')[1].split('&')[0] + '&'

    if(base_params.find('user=') != -1):   
        atributes = atributes + 'user' + base_params.split('user')[1].split('&')[0] + '&'
    
    if(base_params.find('f=') != -1):   
        atributes = atributes + 'f' + base_params.split('f')[1].split('&')[0] + '&'

    if(base_params.find('s=') != -1):   
        atributes = atributes + 's' + base_params.split('s')[1].split('&')[0] + '&'

    atributes = atributes + 'p='
    
    total_pages = getTotalPages(getHtml(base_url))

    for i in range(1, total_pages + 1):
        url_gen = base_url + atributes + str(i)
        html = getHtml(url_gen)
        page = getPageData(html)

       
    pasteTotal(base_url + atributes + str(1), page)

    print('Excel файл \'' + page + '.csv\' успешно создан! ')

if __name__ == '__main__':
    path = input('Введите url адрес с сайта avito: ')
    main(path)

