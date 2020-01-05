import requests
import mysql.connector

from bs4 import BeautifulSoup
from datetime import datetime


BASE_URL = 'https://lardi-trans.com/ajax/reliability_zone/firm/search/'
ULTRA_BASE_URL = 'https://lardi-trans.com'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}


class Parser:
    def __init__(self) -> None:
        self.PAGINATED_LINKS = []
        # Create session and bind headers
        self.__session = requests.Session()
        self.__session.headers.update(HEADERS)

        # Add conditions
        self.reviews_condition = True
        self.company_exist = True

    def parse_all(self):
        # Initial url
        urls = ['https://lardi-trans.com/reliability_zone/search_responses/?firmType=undefined&responseRate=all&page=']

        response = self.__session.get(urls[0] + '1').content
        soup = BeautifulSoup(response, 'lxml')

        # Get max page
        pages = int(soup.find('ul', attrs={
            'class': 'pagination'
        }).find_all('li')[-2].text.strip())

        # Generate paginated pages
        for item in range(1, pages + 1):
            urls.append(urls[0] + f'{item}')

        urls = urls[1:]

        # For even url
        for url in urls:
            even_response = self.__session.get(url).content
            even_soup = BeautifulSoup(even_response, 'lxml')

            all_divs = even_soup.find('div', attrs={
                'class': 'rz-feedback_tab-container'
            }).find_all('div', attrs={
                'class': 'rz-feedback_item'
            })

            # Get needed content
            for div in all_divs:
                date = div.find('span', attrs={
                    'class': 'rz-feedback_service-date'
                }).text.strip()
                from_country = div.find('span', attrs={
                    'class': 'rz-feedback_country-from'
                }).text.strip()
                to_country = div.find('span', attrs={
                    'class': 'rz-feedback_country-to'
                }).text.strip()
                from_town = div.find('span', attrs={
                    'class': 'rz-feedback_town-from'
                }).text.strip()
                to_town = div.find('span', attrs={
                    'class': 'rz-feedback_town-to'
                }).text.strip()
                date_some = div.find('span', attrs={
                    'class': 'rz-feedback_date'
                }).text.strip()
                date_some = format_date(date_some)

                customer = div.find('div', attrs={
                    'class': 'rz-feedback_service-performer'
                }).find('div', attrs={
                    'class': 'rz-feedback_service-person_name'
                }).find('a').text.strip()
                customer_link = ULTRA_BASE_URL + div.find('div', attrs={
                    'class': 'rz-feedback_service-performer'
                }).find('div', attrs={
                    'class': 'rz-feedback_service-person_name'
                }).find('a')['href']

                client = div.find('div', attrs={
                    'class': 'rz-feedback_service-client'
                }).find('div', attrs={
                    'class': 'rz-feedback_service-person_name'
                }).find('a').text.strip()
                client_link = ULTRA_BASE_URL + div.find('div', attrs={
                    'class': 'rz-feedback_service-client'
                }).find('div', attrs={
                    'class': 'rz-feedback_service-person_name'
                }).find('a')['href']

                content_ad = div.find('div', attrs={
                    'class': 'rz-feedback__short'
                }).text.strip()

                print(date, from_country, to_country, from_town,
                      to_town, customer, customer_link, client, client_link,
                      date_some, content_ad)

    def get_variants(self, string: str) -> dict:
        encoded_string = requests.utils.quote(string)
        url = BASE_URL + f'?query={encoded_string}&excludeCurrent=false'
        response = self.__session.get(url).json()
        return response

    def initial_request(self, string: str) -> tuple:
        self.PAGINATED_LINKS = []
        response = self.get_variants(string)

        try:
            response = response['items'][0]['owner']['id']
            content_url = f'https://lardi-trans.com/reliability_zone/search_responses/?firmFromId={response}&'
            response_content = self.__session.get(content_url).content
            soup = BeautifulSoup(response_content, 'lxml')
            return soup, response
        except IndexError:
            self.company_exist = False
            print('Error. Message uncorrect')

    def get_paginated_links(self, soup: str, some_id: int) -> None:
        content_url = f'https://lardi-trans.com/reliability_zone/search_responses/?firmFromId={some_id}&'
        try:
            pagination = int(soup.select('.pagination')[
                0].find_all('li')[-2].find('a').text.strip())
            print(pagination)

            self.PAGINATED_LINKS.append(content_url)
            for item in range(2, pagination + 1):
                self.PAGINATED_LINKS.append(content_url + f'page={item}')
        except IndexError:
            self.PAGINATED_LINKS = [content_url]
            # self.reviews_condition = False
            print('No paginated pages')

    def get_ads(self, string: str) -> list:
        result_list = []
        try:
            soup, some_id = self.initial_request(string)
            self.get_paginated_links(soup, some_id)

            for item in self.PAGINATED_LINKS:
                response = self.__session.get(item).content
                soup = BeautifulSoup(response, 'lxml')

                ads = soup.find_all('div', attrs={'class': 'rz-feedback_item'})
                for ad in ads:
                    date = ad.find(
                        'span', attrs={'class': 'rz-feedback_date'}).text.strip()
                    town_from = ad.find(
                        'span', attrs={'class': 'rz-feedback_town-from'}).text.strip()
                    town_to = ad.find(
                        'span', attrs={'class': 'rz-feedback_town-to'}).text.strip()
                    short = ad.find(
                        'div', attrs={'class': 'rz-feedback__short'}).text.strip()

                    if short == '':
                        short = '-'

                    result_list.append({
                        'date': format_date(date),
                        'town_from': town_from,
                        'town_to': town_to,
                        'short': short
                    })
            if result_list != []:
                return result_list
            else:
                self.reviews_condition = False
        except TypeError:
            self.company_exist = False
            print('Error. Company does not exist')


# Formate timestamp to usuall date
def format_date(date_string: str) -> str:
    formated_date = int(
        date_string[date_string.find("(") + 1:date_string.find(",") - 3])
    date = datetime.fromtimestamp(
        formated_date).strftime(r'%d-%m-%Y, %H:%M:%S')
    return date


some_obj = Parser()
some_obj.parse_all()
