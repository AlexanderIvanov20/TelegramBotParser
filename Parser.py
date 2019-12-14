import requests
from bs4 import BeautifulSoup


BASE_URL = 'https://lardi-trans.com/ajax/reliability_zone/firm/search/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}


class Parser:
    def __init__(self, text):
        self.PAGINATED_LINKS = []
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        html = self.initial_request(self.session, text)
        self.get_paginated_links(html[0], html[1])
        print(self.PAGINATED_LINKS)

        self.ads = self.get_ads(self.session)

    def initial_request(self, session, string):
        self.PAGINATED_LINKS = []
        encoded_string = requests.utils.quote(string)
        url = BASE_URL + f'?query={encoded_string}&excludeCurrent=false'

        try:
            response = session.get(url).json()['items'][0]['owner']['id']
            content_url = f'https://lardi-trans.com/reliability_zone/search_responses/?firmToId={response}&'
            response_content = session.get(content_url).content
            soup = BeautifulSoup(response_content, 'lxml')
            return soup, response
        except IndexError:
            print('Error. Message uncorrect')

    def get_paginated_links(self, soup, some_id):
        pagination = int(soup.select('.pagination')[
            0].find_all('li')[-2].find('a').text.strip())

        content_url = f'https://lardi-trans.com/reliability_zone/search_responses/?firmToId={some_id}&'
        self.PAGINATED_LINKS.append(content_url)

        for item in range(2, pagination + 1):
            self.PAGINATED_LINKS.append(content_url + f'page={item}')

    def get_ads(self, session):
        result_string = ''
        for item in self.PAGINATED_LINKS:
            response = session.get(item).content
            soup = BeautifulSoup(response, 'lxml')

            ads = soup.find_all('div', attrs={'class': 'rz-feedback_item'})
            for ad in ads:
                performer = ad.find(
                    'div', attrs={'class': 'rz-feedback_service-performer'})
                client = ad.find(
                    'div', attrs={'class': 'rz-feedback_service-client'})

                per_name = performer.find(
                    'div', attrs={'class': 'rz-feedback_service-person_name'}).text.strip()
                cli_name = client.find(
                    'div', attrs={'class': 'rz-feedback_service-person_name'}).text.strip()

                # print(per_name, '|', cli_name, '\n')
                result_string += f'{per_name}-----{cli_name}\n'
        return result_string.strip()
