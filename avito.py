#Version 1.11
#Author: Spone

import requests
from bs4 import BeautifulSoup
import csv
import re
from unidecode import unidecode
from urllib.request import urlopen

coutAds = 0
titles = {
    'title'       : 'Наименование',
    'price'       : 'Цена',
    'date'        : 'Дата',
    'address'     : 'Адрес',
    'description' : 'Описание',
    'url'         : 'URL адрес'
}

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
        return str

    return cutPrice + 'р.'

def getPageData(html):
    soup = BeautifulSoup(html, 'lxml')

    try:    
        fileName = soup.find('a', {'class':'rubricator-list-item-link_current-fnAHj'})['title']
    except Exception as e:
        fileName = 'No_name'

    ads = soup.find_all('div', class_='iva-item-content-UnQQ4')
    writeCsv(titles, fileName) ##write title

    global coutAds
    for ad in ads:

        #TITLES: title, price, date, address, description, url
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
            date = ad.find('div', class_='date-text-VwmJG').text.strip()
        except:
            date = '' 
        try:
            address = ad.find('span', class_='geo-address-QTv9k').text.strip()
        except:
            address = '' 
        try:
            url = 'https://www.avito.ru/' + ad.find('a', {'class':'link-link-MbQDP'})['href']
        except:
            url = '' 
        try:
            description = ad.find('div', class_='iva-item-description-S2pXQ').text.strip()
        except:
            description = ''           

        data = {
            'title'  :title,
            'price'  :price,
            'date'   :date,
            'address':address,
            'url'    :url,
            'description':description
        }

        coutAds += 1
        writeCsv(data, fileName)
        
    return fileName

def writeCsv(data, fileName = 'avito'):

    fileName = str(fileName) +'.csv'
    with open(fileName, 'a', encoding = "cp1251", newline = '', errors = 'replace') as f:
        writer = csv.writer(f, delimiter=';')
      
        writer.writerow((
            data['title'],
            data['price'],
            data['date'],
            data['address'],
            data['description'],
            data['url']
        ))

def pasteTotal(url, fileName = 'avito'):
    text = getHtml(url)
    soup = BeautifulSoup(text, 'lxml') 

    try:        
        nameChapter = soup.find('h1', class_='page-title-inline-zBPFx').text.strip()
    except:
        nameChapter = ''    

    global coutAds
    data = {
        'total': int(coutAds),
        'nameChapter': nameChapter
    }

    writeTotalCsv(data, fileName)       

def writeTotalCsv(data, fileName = 'avito'):

    fileName = str(fileName) +'.csv'
    with open(fileName ,'a', encoding="cp1251", newline='') as f:

        writer = csv.writer(f, delimiter = ';')
        writer.writerow((
            data['nameChapter'],
            data['total'],
            'объявлений'
        ))

def checkCategoryError(path):

    checkCategoryError = 0
    categoryCheck = getHtml(path)
    soup = BeautifulSoup(categoryCheck, 'lxml')

    try:
        check = soup.find('div', class_='item-view-socials')

        if(check):
            checkCategoryError = 1
    except:
        checkCategoryError = 0
    
    return checkCategoryError


def main(path):
    
    if(path.find('avito.ru') == -1):
        print('Вы вставили ссылку не с сайта Avito.ru!')
        return
    
    checkCategory = checkCategoryError(path)

    if(checkCategory):
        print('Вы не выбрали категорию объявлений!')
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