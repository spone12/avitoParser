#https://www.avito.ru/tver/igry_pristavki_i_programmy?p=2
#https://www.youtube.com/watch?v=zlWiw99bBUk

import requests
from bs4 import BeautifulSoup
import csv

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

    ads = soup.find_all('div', class_='item_table-description')
    
    
    for ad in ads:
        #title,price,place
        try:
            title = ad.find('h3').find('a').text.strip() #get('title')
        except:
            title = ''
        try:
            price = ad.find('span', class_='snippet-price ').text
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

        write_csv(data)

    #return ads


def write_csv(data):
    #newline = '' (3 параметр, убрать разделение между строками)
    with open('avito.csv','a') as f:
        writer = csv.writer(f, delimiter=';')
        
        writer.writerow((data['title'],
                         data['price'],
                         data['data'],
                         data['url']
                         ))


def main(path):
    
    base_url = path.split('?')[0] + '?' #'https://www.avito.ru/tver/igry_pristavki_i_programmy?p=1'
    #atributes = path.split('?')[1].split('=')[0] + '='
    #atributes2 = path.split('?')[1].split('=')[2] + '='
    atributes2 = ''

    if (path.find('&') != -1): 
        atributes = path.split('?')[1].split('&')[0].split('=')[0] + '=1'
        atributes2 = path.split('?')[1].split('&')[1].split('=')[0] + '='
    else:
        atributes = path.split('?')[1].split('=')[0] + '=1&p='    
    
    total_pages = get_total_pages(get_html(base_url))

    for i in range(1, total_pages + 1):
    #for i in range(1, 2 + 1):
        if atributes2:
            url_gen = base_url + atributes + '&' + atributes2 + str(i)
        else:
            url_gen = base_url + atributes + str(i)

        html = get_html(url_gen)
        page = get_page_data(html)

        #print(page)

if __name__ == '__main__':
    path = input('Введите url адрес с сайта avito: ')
    main(path)

