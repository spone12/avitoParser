#Cоздание заголовка с названием региона + радиус
#version 1.6

#Spone 22.02.20
#1.1 Добавлен ввод url
#1.2 Добавлено имя файла.csv
#1.3 Исправлена ошибка с отображением цены товара
#1.4 Вывод сообщения о создании файла
#1.5 Проверка на корректность ссылки (параметры) и что является сайтом avito
#1.6 Полностью переписана структура параметров, добавлен радиус и геолокация
#1.7 Убрана завязка на количество страниц, теперь если только одна страница, то берётся только с неё

import requests
from bs4 import BeautifulSoup
import csv
import re
from unidecode import unidecode

def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    
    
    try:
        pages = soup.find_all('span', class_='pagination-item-1WyVp')[-2].get('data-marker')
        p = pages.split('(')[1].split(')')[0]
    except:
        p = 1

    return int(p)



def delete_symbol(str):
    return re.sub(r'[^0-9.]+', r'', str)



def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')

    name_file = soup.find('a', class_='rubricator-list-item-link_current-25dGP').text.strip()
    ads = soup.find_all('div', class_='item_table-description')
    
    
    for ad in ads:
        #title,price,place
        try:
            title = ad.find('h3').find('a').text.strip() #get('title')
        except:
            title = ''
        try:
            pr = ad.find('span', class_='snippet-price').text.strip()
            price = delete_symbol(pr) + 'р.'

            #valuta = ad.find('span', class_='font_arial-rub').text.strip()
            
           # price = price + ' ' + valuta
        except:
            price = ''    
        try:
            #https://charbase.com/00b2-unicode-superscript-two charbase
            #https://www.avito.ru/tver/komnaty?cd=1
            url = 'https://www.avito.ru/' +  ad.find('h3').find('a').get('href').strip()

            #url = url.encode(encoding='utf-8', errors='ignore').decode('cp1251', 'ignore')
            #\u00b2
            #a = u"1\u005c\u0078\u0062\u0032"
            #a = a.encode('UTF-8').decode('UTF-8').encode('cp1251')
            #url = unicode(u'\xb2', 'unicode-escape')
            #url = unidecode(url)
            #url = unicode.encode( url, "cp1251" )
           
            
        except:
            url = '' 
        try:
            data = ad.find('div', class_='snippet-date-info').text.strip()
        except:
            data = ''           

        data = {'title':title,
                'price':price,
                'url':url,
                'data':data}
    
        write_csv(data, name_file)

    return name_file
    #return ads


def write_csv(data, name_file = 'avito'):
    #newline = '' (3 параметр, убрать разделение между строками)
    #encoding='utf-8'
    with open(str(name_file) +'.csv','a', encoding="cp1251", newline='') as f:
        writer = csv.writer(f, delimiter=';')
      

        writer.writerow((data['title'],
                         data['price'],
                         data['data'],
                         data['url']
                         ))


def main(path):
    
    if(path.find('avito.ru') == -1):
        print('Вы вставили ссылку не с сайта Avito.ru!')
        return
    if(path.find('?') == -1):
        print('Ваша URL ссылка не имеет параметров! Парсинг невозможен!')
        return

    base_url = path.split('?')[0] + '?' #'https://www.avito.ru/tver/igry_pristavki_i_programmy?'
    base_params = path.split('?')[1]

    #p = re.compile('=')
    #col_params = len(p.findall(base_params))
    #print(col_params)
    
    atributes = ''   
    if(base_params.find('cd=') != -1):
        atributes = atributes + 'cd' + base_params.split('cd')[1].split('&')[0] + '&'   

    if(base_params.find('radius=') != -1):    
        atributes = atributes + 'radius' + base_params.split('radius')[1].split('&')[0] + '&'
   
    
    if(base_params.find('geoCoords=') != -1):   
        atributes = atributes + 'geoCoords' + base_params.split('geoCoords')[1].split('&')[0] + '&'

    atributes = atributes + 'p='

    total_pages = get_total_pages(get_html(base_url))

    for i in range(1, total_pages + 1):
    #for i in range(1, 3):
       
        url_gen = base_url + atributes + str(i)

        html = get_html(url_gen)
        page = get_page_data(html)

    print('Excel файл \'' + page + '.csv\' успешно создан! ')

if __name__ == '__main__':
    path = input('Введите url адрес с сайта avito: ')
    main(path)

