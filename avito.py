#Cоздание заголовка с названием региона + радиус
#version 1.6

#Spone 22.02.20
#1.1 Добавлен ввод url
#1.2 Добавлено имя файла.csv
#1.3 Исправлена ошибка с отображением цены товара
#1.4 Вывод сообщения о создании файла
#1.5 Проверка на корректность ссылки (параметры)
#1.6 Полностью переписана структура параметров, добавлен радиус и геолокация

import requests
from bs4 import BeautifulSoup
import csv
import re

def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    
    pages = soup.find_all('span', class_='pagination-item-1WyVp')[-2].get('data-marker')
    p = pages.split('(')[1].split(')')[0]
    return int(p)


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
            price = re.sub(r'[^0-9.]+', r'', pr)

            #valuta = ad.find('span', class_='font_arial-rub').text.strip()
            
           # price = price + ' ' + valuta
        except:
            price = ''    
        try:
            url = 'https://www.avito.ru/' +  ad.find('h3').find('a').get('href')
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
    with open(str(name_file) +'.csv','a', encoding="cp1251") as f:
        writer = csv.writer(f, delimiter=';')
        
        writer.writerow((data['title'],
                         data['price'],
                         data['data'],
                         data['url']
                         ))


def main(path):
    
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

