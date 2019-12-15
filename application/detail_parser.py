import json
import re

from parsel import Selector
from six.moves.html_parser import HTMLParser


class DetailParser(object):

    def __init__(self, text, type='html', namespaces=None, root=None, base_url=None):
        self.selector = Selector(
            text, type=type, namespaces=namespaces, root=root, base_url=base_url)
        self.html_parser = HTMLParser()

    def parse(self):
        return {
            'title': self.parse_title(),
            'author': self.parse_author(),
            'feature_bullets': self.parse_feature_bullets(),
            'book_description': self.parse_book_description(),
            'product_description': self.parse_product_description(),
            'big_images': self.parse_big_images(),
            'little_images': self.parse_little_images(),
            'star': self.parse_star(),
            'reviews': self.parse_reviews(),
            'rank': self.parse_rank(),
            'categories': self.parse_categories(),
            'details': self.parse_details(),
            'bylines': self.parse_bylines()
        }

    def parse_title(self):
        raw_title = self.selector.xpath('//*[@id="productTitle"]/text()').get()
        return raw_title.strip() if raw_title else ''

    def parse_author(self):
        author_elems = self.selector.xpath('//a[@id="bylineInfo"]/text()')
        author_elems.extend(self.selector.xpath(
            '//*[@id="bylineInfo"]/span[contains(@class, "author")]/a/text()'))
        xpath_str = '//*[@id="bylineInfo"]/span[contains(@class, "author")]'
        xpath_str += '//a[contains(@class, "contributorNameID")]/text()'
        author_elems.extend(self.selector.xpath(xpath_str))
        xpath_str = '//*[@id="byline"]/span[contains(@class, "author")]'
        xpath_str += '//a[contains(@class, "contributorNameID")]/text()'
        author_elems.extend(self.selector.xpath(xpath_str))
        # xpath_str = '//*[@id="bylineInfo"]/span[contains(@class, "author")]'
        # xpath_str += '/a[contains(@class, "a-link-normal")]/text()'
        # author_elems.extend(self.selector.xpath(xpath_str))

        return author_elems.getall()

    def parse_bylines(self):
        bylines = dict()
        xpath_str = '//*[@id="bylineInfo"]/span[@class="a-color-secondary"]'
        byline_elems = self.selector.xpath(xpath_str)
        byline_elems.extend(self.selector.xpath(
            '//*[@id="bylineInfo"]/span[@class="a-color-secondary"]'))
        for byline_elem in byline_elems:
            key = byline_elem.xpath('./text()').get().strip().strip(':')
            value = byline_elem.xpath('./following-sibling::span/text()').get()
            value = value.strip() if value else ''
            if key and value:
                bylines[key] = value

        return bylines

    def parse_feature_bullets(self):
        raw_bullets = self.selector.xpath(
            '//*[@id="feature-bullets"]/ul/li/span[contains(@class, "a-list-item")]/text()').getall()
        return [s.strip().replace(u'\xa0', ' ') for s in raw_bullets if s and not s.isspace()]

    def parse_book_description(self):
        noscript_elems = self.selector.xpath('//*[@id="bookDescription_feature_div"]/noscript')
        return ''.join([s.strip() for s in noscript_elems.xpath('.//text()').getall()])

    def parse_product_description(self):
        try:
            des = self.selector.xpath('//*[@id="productDescription"]/p//text()').getall()
            product_description = ''.join([s.strip() for s in des])
        except:
            product_description = ''

        return product_description

    def parse_big_images(self):
        thumb_urls = []

        bottom_thumb_elems = self.selector.xpath(
            '//*[@id="imageBlockThumbs"]//div[contains(@class, "imageThumb")]/img')
        bottom_thumb_urls = bottom_thumb_elems.xpath('./@src').getall()
        thumb_urls.extend(bottom_thumb_urls)

        if len(thumb_urls) < 0:
            front_img_data = self.selector.xpath(
                '//img[@id="imgBlkFront"]/@data-a-dynamic-image').get()
            if front_img_data:
                front_img_data = self.html_parser.unescape(front_img_data)
                try:
                    front_img_dict = json.loads(front_img_data)
                    thumb_urls.extend(list(front_img_dict.keys()))
                except:
                    pass

        return thumb_urls

    def parse_little_images(self):
        thumb_urls = []

        bottom_thumb_elems = self.selector.xpath(
            '//*[@id="main-image-container"]//li//img')
        bottom_thumb_urls = bottom_thumb_elems.xpath('./@data-old-hires').getall()
        thumb_urls.extend(bottom_thumb_urls)

        side_thumb_elems = self.selector.xpath(
            '//*[@id="altImages"]//li[contains(@class, "item")]//img')
        side_thumb_urls = side_thumb_elems.xpath('./@src').getall()
        thumb_urls.extend(side_thumb_urls)

        if len(thumb_urls) <= 0:
            front_img_data = self.selector.xpath(
                '//img[@id="imgBlkFront"]/@data-a-dynamic-image').get()
            if front_img_data:
                front_img_data = self.html_parser.unescape(front_img_data)
                try:
                    front_img_dict = json.loads(front_img_data)
                    thumb_urls.extend(list(front_img_dict.keys()))
                except:
                    pass

        return thumb_urls

    def parse_star(self):
        stars = 0
        stars_str = self.selector.xpath('//*[@id="acrPopover"]/@title').get()
        try:
            stars = float(stars_str.strip().split().pop(0))
        except:
            pass

        return stars

    def parse_reviews(self):
        reviews = 0
        reviews_str = self.selector.xpath(
            '//*[@id="acrCustomerReviewText"]/text()').get()
        try:
            reviews = int(reviews_str.strip().split().pop(0))
        except:
            pass

        return reviews

    def parse_details(self):
        details = dict()

        details_elems = self.selector.xpath(
            '//*[@id="productDetailsTable"]/tr/td/div[@class="content"]/ul/li[not(@id="SalesRank")]')
        for details_elem in details_elems:
            key = details_elem.xpath('./b/text()').get()
            key = key.strip().strip(':') if key else ''
            if key == 'Format':
                value = details_elem.xpath('./a/text()').get()
            elif key == 'Other Editions' or key == 'Weitere Ausgaben' or \
                    key.find('Autres versions') != -1:
                value = ' | '.join(details_elem.xpath('./a/text()').getall())
            else:
                value = details_elem.xpath('./text()').get()
            value = value.strip() if value else ''
            if key and value:
                details[key] = value

        details_elems = self.selector.xpath(
            '//*[@id="detailBullets_feature_div"]/ul/li/span[@class="a-list-item"]')
        for details_elem in details_elems:
            key = details_elem.xpath('./span[@class="a-text-bold"]/text()').get()
            key = key.strip().strip(':') if key else ''
            value = details_elem.xpath(
                './span[not(@class="a-text-bold")]/text()').get()
            value = value.strip() if value else ''
            if key and value:
                details[key] = value

        details_elems = self.selector.xpath(
            '//*[@id="productDetails_detailBullets_sections1"]/tbody/tr')
        for details_elem in details_elems:
            key = details_elem.xpath('./th/text()').get()
            key = key.strip().strip(':') if key else ''
            value = details_elem.xpath('./td/text()').get()
            value = value.strip() if value else ''
            if key and value:
                details[key] = value

        details_elems = self.selector.xpath('//div[@id="prodDetails"]//table//tr')
        for details_elem in details_elems:
            key = details_elem.xpath('./th[contains(@class, "prodDetSectionEntry")]/text()').get()
            key = key.strip().strip(':') if key else ''
            value = details_elem.xpath('./td/text()').get()
            value = value.strip() if value else ''
            if key and value:
                details[key] = value

        details_elems = self.selector.xpath(
            '//div[@id="detail-bullets"]/table/tr/td/div[@class="content"]/ul/li')
        for details_elem in details_elems:
            key = details_elem.xpath('./b/text()').get()
            key = key.strip().strip(':') if key else ''
            if key == 'Actors':
                value = ','.join(details_elem.xpath('./a/text()').getall())
            else:
                value = ''.join(details_elem.xpath('./text()').getall())
            value = value.strip() if value else ''
            if key and value:
                if key == 'Region':
                    value = value.split('(').pop(0).strip()
                details[key] = value

        details_elems = self.selector.xpath(
            '//div[@id="detail_bullets_id"]/table/tr/td/div[@class="content"]/ul/li')
        for details_elem in details_elems:
            key = details_elem.xpath('./b/text()').get()
            key = key.strip().strip(':') if key else ''
            if key == 'Other Editions' or key == 'Weitere Ausgaben' or \
                    key.find('Autres versions') != -1:
                value = ' | '.join(details_elem.xpath('./a/text()').getall())
            else:
                value = ''.join(details_elem.xpath('./text()').getall())
            value = value.strip() if value else ''
            if key and value:
                details[key] = value

        details_elems = self.selector.xpath(
            '//div[@id="prodDetails"]//div[@class="pdTab"]/table//tr')
        for details_elem in details_elems:
            key = details_elem.xpath('./td[@class="label"]/text()').get()
            key = key.strip().strip(':') if key else ''
            value = details_elem.xpath('./td[@class="value"]/text()').get()
            value = value.strip() if value else ''
            if key and value:
                details[key] = value

        if 'Shipping Weight' in details:
            details['Shipping Weight'] = details['Shipping Weight'].replace(
                '(', '').replace(')', '').strip()

        if 'Region' in details:
            details['Region'] = details['Region'].split('(').pop(0).strip()

        for k in [
            'Amazon Bestsellers Rank', 'Amazon Best Sellers Rank',
            'Average Customer Review', 'Customer Reviews']:
            if k in details:
                details.pop(k)

        result = dict()
        for k, v in details.items():
            result[k.strip().replace(u'\xa0', '')] = v

        return result

    def parse_specifications(self):
        pass

    def parse_categories(self):
        categories = []
        category_wrappers = self.selector.xpath(
            '//*[@id="SalesRank"]/ul[@class="zg_hrsr"]/li')
        for category_wrapper in category_wrappers:
            categories.append('>'.join(
                category_wrapper.xpath('./span[@class="zg_hrsr_ladder"]//a/text()').getall()))

        category_wrappers = self.selector.xpath(
            '//*[@id="SalesRank"]/td[@class="value"]/ul[@class="zg_hrsr"]/li')
        for category_wrapper in category_wrappers:
            categories.append('>'.join(
                category_wrapper.xpath('./span[@class="zg_hrsr_ladder"]//a/text()').getall()))

        xpath_str = '//*[@id="prodDetails"]//table//tr'
        xpath_str += '/th[contains(@class, "prodDetSectionEntry") and '
        xpath_str += 'contains(./text(), "Best Sellers Rank")]'
        xpath_str += '/following-sibling::td'
        category_wrappers = self.selector.xpath(xpath_str).xpath('./span/span')
        try:
            category_wrappers.pop(0)
        except IndexError:
            pass
        for category_wrapper in category_wrappers:
            categories.append('>'.join(category_wrapper.xpath('./a/text()').getall()))

        return ';'.join(categories)

    def parse_rank(self):
        sales_rank_str = ''.join(
            self.selector.xpath('//*[@id="SalesRank"]/text()').getall()).strip()
        if not sales_rank_str:
            raw_sales_rank_str = ''.join(
                self.selector.xpath('//*[@id="SalesRank"]/td[@class="value"]/text()').getall())
            sales_rank_str = raw_sales_rank_str.strip()
        if sales_rank_str:
            try:
                rank = int(re.sub(r'[#,\.]', '', sales_rank_str.replace('Nr. ', '').split().pop(0)))
            except:
                rank = 0
        else:
            common_xpath_str = '//*[@id="prodDetails"]//table//tr'
            common_xpath_str += '/th[contains(@class, "prodDetSectionEntry") and '
            common_xpath_str += 'contains(./text(), "Best Sellers Rank")]/following-sibling::td'
            sales_rank_str = ''.join(
                self.selector.xpath(common_xpath_str).xpath('./span/span/text()').getall()).strip()
            if sales_rank_str:
                try:
                    rank = int(
                        re.sub(r'[#,\.]', '', sales_rank_str.replace('Nr. ', '').split().pop(0)))
                except:
                    rank = 0
            else:
                rank = 0

        return rank
