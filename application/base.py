import random
from typing import Dict, List

import requests

from config import SHOPS_SETTINGS


class Shop:
    """Общий класс для парсинга магазинов"""

    def __init__(self, name):
        self.name = name
        self.requests = requests
        self.session = requests.Session()
        self.shop_setting = SHOPS_SETTINGS[self.name]
        self.session_setting = SHOPS_SETTINGS['Session']

    def __repr__(self):
        return '{}'.format(self.name)

    def random_headers(self):
        headers = {'User-Agent': random.choice(self.session_setting['user_agent']),
                   'Accept': self.session_setting['accept']}
        self.session.headers.update(headers)

    def count_control(self, result, lower_value=1):
        """
        Подсчитывает количество полученных ответов,
        пишет лог
        :param result: полученные ответы от апи магазина
        :param lower_value: нижнее значение
        :return:
        """
        count = len(result)
        if count > lower_value:
            msg = "количество ответов asins: {}".format(count)
            print('info', msg)
        else:
            msg = "низкое количество ответов от asins: {}".format(count)
            print('error', msg)

    def parsing(self) -> List[Dict]:
        raise NotImplementedError
