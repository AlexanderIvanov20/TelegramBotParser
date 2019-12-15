import requests
from bs4 import BeautifulSoup
from datetime import datetime


BASE_URL = 'https://lardi-trans.com/ajax/reliability_zone/firm/search/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}


class Parser:
    def __init__(self) -> None:
        self.PAGINATED_LINKS = []
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.reviews_condition = True
        self.company_exist = True

    def get_variants(self, string: str) -> dict:
        encoded_string = requests.utils.quote(string)
        url = BASE_URL + f'?query={encoded_string}&excludeCurrent=false'
        response = self.session.get(url).json()
        return response

    def initial_request(self, string: str) -> tuple:
        self.PAGINATED_LINKS = []
        response = self.get_variants(string)

        try:
            response = response['items'][0]['owner']['id']
            content_url = f'https://lardi-trans.com/reliability_zone/search_responses/?firmFromId={response}&'
            response_content = self.session.get(content_url).content
            soup = BeautifulSoup(response_content, 'lxml')
            return soup, response
        except IndexError:
            self.company_exist = False
            print('Error. Message uncorrect')

    def get_paginated_links(self, soup: str, some_id: int) -> None:
        try:
            pagination = int(soup.select('.pagination')[
                0].find_all('li')[-2].find('a').text.strip())

            content_url = f'https://lardi-trans.com/reliability_zone/search_responses/?firmFromId={some_id}&'
            self.PAGINATED_LINKS.append(content_url)

            for item in range(2, pagination + 1):
                self.PAGINATED_LINKS.append(content_url + f'page={item}')
        except IndexError:
            self.PAGINATED_LINKS = []
            self.reviews_condition = False
            print('Index error')

    def get_ads(self, string: str) -> list:
        result_list = []
        try:
            soup, some_id = self.initial_request(string)
            self.get_paginated_links(soup, some_id)

            for item in self.PAGINATED_LINKS:
                response = self.session.get(item).content
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
            return result_list
        except TypeError:
            self.company_exist = False
            print('Error. Company does not exist')


def format_date(date_string: str) -> str:
    formated_date = int(
        date_string[date_string.find("(") + 1:date_string.find(",") - 3])
    date = datetime.fromtimestamp(
        formated_date).strftime(r'%d-%m-%Y, %H:%M:%S')
    return date
