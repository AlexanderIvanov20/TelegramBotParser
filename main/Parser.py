import requests
import mysql.connector as mysql_conn
from sys import argv as sys_args
from bs4 import BeautifulSoup
from datetime import datetime
from random import sample, choice
import os.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


BASE_URL = 'https://lardi-trans.com/ajax/reliability_zone/firm/search/'
ULTRA_BASE_URL = 'https://lardi-trans.com'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                  '537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 '
                  'Safari/537.36'
}
with open(os.path.join(BASE_DIR, 'proxies.txt'), 'r', encoding='utf-8') as file:
    data = file.readlines()

PROXIES = []
for item in data:
    PROXIES.append(item.strip())
print(PROXIES)

PROXY = {
    'http': str(choice(PROXIES))
}
CONNECTION = mysql_conn.connect(user='root', password='myrootpassword',
                                host='localhost', database='database1',
                                auth_plugin='mysql_native_password')


class Parser:
    def __init__(self) -> None:
        self.PAGINATED_LINKS = []
        # Create session and bind headers
        self.__session = requests.Session()
        self.__session.headers.update(HEADERS)
        self.__session.proxies = PROXY

        # Add conditions
        self.reviews_condition = True
        self.company_exist = True

    def parse_all(self) -> None:
        # Initial url
        urls = [
            'https://lardi-trans.com/reliability_zone/search_responses/'
            '?firmType=undefined&responseRate=negative&page='
        ]

        # Do get request
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

        count = 0
        # For even url
        CURSOR = CONNECTION.cursor()
        for url in urls:
            even_response = self.__session.get(url).content
            even_soup = BeautifulSoup(even_response, 'lxml')

            try:
                template_write_to_database(even_soup=even_soup)
            except Exception as error:
                self.__session.proxies = {
                    'http': str(choice(PROXIES))
                }
                even_response = self.__session.get(url).content
                even_soup = BeautifulSoup(even_response, 'lxml')

                template_write_to_database(even_soup=even_soup, CURSOR=CURSOR)
            print(count)
            count += 1
        CURSOR.close()

    def additional_pages(self):
        url = ('https://lardi-trans.com/reliability_zone/search_responses/'
               '?firmType=undefined&responseRate=negative&page=1')

        # Do get request
        response = self.__session.get(url).content
        soup = BeautifulSoup(response, 'lxml')

        CURSOR = CONNECTION.cursor()

        # Get all cooments on page
        template_write_to_database(even_soup=soup, CURSOR=CURSOR)
        CURSOR.close()

    def get_variants(self, string: str) -> dict:
        encoded_string = requests.utils.quote(string)
        url = BASE_URL + f'?query={encoded_string}&excludeCurrent=false'
        response = self.__session.get(url).json()
        return response

    # def initial_request(self, string: str) -> tuple:
    #     self.PAGINATED_LINKS = []
    #     response = self.get_variants(string)

    #     try:
    #         response = response['items'][0]['owner']['id']
    #         content_url = ('https://lardi-trans.com/reliability_zone/'
    #                        f'search_responses/?firmFromId={response}&')
    #         response_content = self.__session.get(content_url).content
    #         soup = BeautifulSoup(response_content, 'lxml')
    #         return soup, response
    #     except IndexError:
    #         self.company_exist = False
    #         print('Error. Message uncorrect')

    # def get_paginated_links(self, soup: str, some_id: int) -> None:
    #     content_url = ('https://lardi-trans.com/reliability_zone/'
    #                    f'search_responses/?firmFromId={some_id}&')
    #     try:
    #         pagination = int(soup.select(
    #             '.pagination'
    #         )[0].find_all('li')[-2].find('a').text.strip())
    #         print(pagination)

    #         self.PAGINATED_LINKS.append(content_url)
    #         for item in range(2, pagination + 1):
    #             self.PAGINATED_LINKS.append(content_url + f'page={item}')
    #     except IndexError:
    #         self.PAGINATED_LINKS = [content_url]
    #         # self.reviews_condition = False
    #         print('No paginated pages')


# Formate timestamp to usuall date
def format_date(date_string: str) -> str:
    formated_date = int(
        date_string[date_string.find("(") + 1:date_string.find(",") - 3]
    )
    date = datetime.fromtimestamp(
        formated_date
    ).strftime(r'%d.%m.%Y')
    return date


def template_write_to_database(even_soup, CURSOR):
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
        }).text.strip().replace("'", '')
        to_town = div.find('span', attrs={
            'class': 'rz-feedback_town-to'
        }).text.strip().replace("'", '')
        date_some = div.find('span', attrs={
            'class': 'rz-feedback_date'
        }).text.strip()
        date_some = format_date(date_some)

        customer = div.find('div', attrs={
            'class': 'rz-feedback_service-performer'
        }).find('div', attrs={
            'class': 'rz-feedback_service-person_name'
        }).find('a').text.strip().replace("'", '')
        customer_link = ULTRA_BASE_URL + div.find('div', attrs={
            'class': 'rz-feedback_service-performer'
        }).find('div', attrs={
            'class': 'rz-feedback_service-person_name'
        }).find('a')['href']

        client = div.find('div', attrs={
            'class': 'rz-feedback_service-client'
        }).find('div', attrs={
            'class': 'rz-feedback_service-person_name'
        }).find('a').text.strip().replace("'", '')
        client_link = ULTRA_BASE_URL + div.find('div', attrs={
            'class': 'rz-feedback_service-client'
        }).find('div', attrs={
            'class': 'rz-feedback_service-person_name'
        }).find('a')['href']

        content_ad = div.find('div', attrs={
            'class': 'rz-feedback__short'
        }).text.strip().replace("'", '')

        if content_ad == '' or content_ad == '' or \
                client.strip() == '' or from_town == '-' or \
                to_town == '-' or \
                client_link == 'https://lardi-trans.com/user/0/':
            pass
        else:
            try:
                CURSOR.execute(
                    "INSERT INTO database1.telegram_parser_comment"
                    "(town_from, town_to, posted, date, country_from, "
                    "country_to, customer, customer_link, recipient, "
                    f"recipient_link, short) VALUES('{from_town}', "
                    f"'{to_town}', '{date_some}', '{date}', "
                    f"'{from_country}', '{to_country}', '{customer}', "
                    f"'{customer_link}', '{client}', '{client_link}', "
                    f"'{content_ad}')"
                )
                CONNECTION.commit()
            except Exception as error:
                print(error)


if __name__ == '__main__':
    parser = Parser()
    try:
        mode = sys_args[1]
    except KeyError:
        parser.parse_all()
    if mode == 'add':
        parser.additional_pages()
