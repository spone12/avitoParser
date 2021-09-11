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

coutAds = 0
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

    cutPrice = re.sub(r'[^0-9.]+', r'', str)
    if not cutPrice:
        return 'Цена не указана'

    return cutPrice + 'р.'

def getPageData(html):
    soup = BeautifulSoup(html, 'lxml')

    try:    
        name_file = soup.find('a', {'class':'rubricator-list-item-link_current-fnAHj'})['title']
    except Exception as e:
        name_file = 'None'

    ads = soup.find_all('div', class_='iva-item-content-UnQQ4')
    writeCsv(titles, name_file) ##write title

    global coutAds
    for ad in ads:
        #title,price, description, url
        try:
            title = ad.find('h3', class_='title-root-j7cja').text.strip()
        except:
            title = ''
        try:
            pr = ad.find('span', class_='price-text-E1Y7h').text.strip()
            price = deleteSymbol(pr)
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

        coutAds += 1
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
        nameChapter = soup.find('h1', class_='page-title-inline-zBPFx').text.strip()
    except:
        nameChapter = ''    

    global coutAds
    data = {'total': int(coutAds),
            'nameChapter': nameChapter
           }

    write_shapka_csv(data,name_file)       

def write_shapka_csv(data, name_file = 'avito'):
    #newline = '' (3 параметр, убрать разделение между строками)
    with open(str(name_file) +'.csv','a', encoding="cp1251", newline='') as f:

        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['nameChapter'],
                         data['total'],
                         'объявлений'
                         ))

def main(path):
    
    if(path.find('avito.ru') == -1):
        print('Вы вставили ссылку не с сайта Avito.ru!')
        return

    if(path.find('?') == -1):
        path += '?' 

    base_url = path.split('?')[0] + '?' #link before parametrs
    base_params = path.split('?')[1] #attributes
    atributes = base_params + '&p='
    
    total_pages = getTotalPages(getHtml(path))

    for i in range(1, total_pages + 1):
        url_gen = base_url + atributes + str(i)
        html = getHtml(url_gen)
        page = getPageData(html)

    pasteTotal(base_url + atributes + str(1), page)

    print('Excel файл \'' + page + '.csv\' успешно создан! ')

if __name__ == '__main__':
    path = input('Введите url адрес с сайта avito: ')
    main(path)

