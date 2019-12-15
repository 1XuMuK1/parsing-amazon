#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re

from application.base import Shop
from application.detail_parser import DetailParser
# from application.helpers.proxy_list_for_test import proxy
from lxml import html
from json import dump, loads
from re import sub
from dateutil import parser as dateparser
from time import sleep

from application.helpers.proxy import get_proxies


class Amazon(Shop):
    def __init__(self):
        super().__init__('Amazon')
        self.random_headers()
        self.url = self.shop_setting['url']

    def get_data(self, asin: str, proxy=None):
        if not proxy:
            list_proxies = get_proxies()
            proxy = random.choice(list_proxies)
        self.url = self.url + asin
        try:
            response = self.session.get(self.url, verify=False, timeout=30, proxies={'https': f'{proxy}'})
            if response.status_code == 404:
                return {"url": self.url, "error": "page not found"}
            if response.status_code != 200:
                return {"url": self.url, "error": "page not found"}
            return response
        except:
            print('line 32 ', self.url)

    def product_name(self, parser):
        xpath = '//h1//span[@id="productTitle"]//text()'
        raw_product_name = parser.xpath(xpath)
        product_name = ''.join(raw_product_name).strip()
        return product_name

    def product_price(self, parser):
        xpath = '//span[@id="priceblock_ourprice"]/text()'
        raw_product_price = parser.xpath(xpath)
        product_price = ''.join(raw_product_price).replace(',', '')
        return product_price

    def ratings_dict(self, parser):
        ratings_dict = {}
        xpath = '//table[@id="histogramTable"]//tr'
        total_ratings = parser.xpath(xpath)
        for ratings in total_ratings:
            extracted_rating = ratings.xpath('./td//a//text()')
            if extracted_rating:
                rating_key = extracted_rating[0]
                raw_raing_value = extracted_rating[1]
                rating_value = raw_raing_value
                if rating_key:
                    ratings_dict.update({rating_key: rating_value})
        return ratings_dict

    @staticmethod
    def details(cleaned_response):
        return DetailParser(cleaned_response).parse()

    def size(self):
        pass

    def sections(self):
        pass

    def colors(self):
        pass

    def parse_reviews(self, response, asin):
        try:
            # Избавляемся от нулевых байтов
            cleaned_response = response.text.replace('\x00', '')

            parser = html.fromstring(cleaned_response)

            data = {
                'asin': asin,
                'url': self.url,
                'sections': self.sections(),
                'name': self.product_name(parser),
                'price': self.product_price(parser),
                'ratings': self.ratings_dict(parser),
                'size': self.size(),
                'colors': self.colors(),
                # TODO: в details нужно еще собирать большие картинки
                'details': self.details(cleaned_response),

            }
            return data
        except:
            return {"url": self.url, "error": "failed to process the page"}

    def parsing(self, _proxy=None):
        # user_agent https://udger.com/resources/ua-list/browser-detail?browser=Chrome
        # proxies https://free-proxy-list.net/
        # Добавление ASINs для парсинга определенной вещи
        result = []
        # запрос в бд за asins

        asins = ['B07G7FNVG3']

        for asin in asins:
            print("Downloading and processing page http://www.amazon.com/dp/" + asin)
            response = self.get_data(asin, _proxy)
            result.append(self.parse_reviews(response, asin))
            sleep(5)

        f = open('data.json', 'w')
        dump(result, f, indent=4)
        f.close()
        return result


if __name__ == '__main__':
    Amazon().parsing(_proxy='36.89.192.115:56432')
