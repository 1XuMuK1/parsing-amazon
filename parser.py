from typing import Dict, List

import click
from sqlalchemy.exc import SQLAlchemyError

from application.helpers.shops import shops
from application.helpers.exceptions import ShopBadResponseException, ShopTokenException, \
    ShopApiException, ShopManualParsingException
from application.helpers.models import ItemsShop, connect_db
from application.helpers.shops import manual_shops


def save_shops_data(parsing_results: List[Dict], shop_name: str) -> None:
    """Сохраняет результат парсинга магазина в заданную таблицу"""
    session, _engine = connect_db(echo=False)
    for result in parsing_results:
        session.add(ItemsShop(**result, shop_name=shop_name))
    session.commit()
    session.close()


def manual_parsing(proxies, shop_name):
    """
    Amazon использует защиту от роботов.
    Как вариант решения этой проблемы, вынесем получения токена в ручной режим.
    """
    try:
        shop = get_shop(shop_name)
        msg = 'парсинг магазина: {}'.format(shop.name)
        print(msg)
        parsing_results = shop.parsing(proxies)
        save_shops_data(parsing_results, shop.name)
    except (ShopBadResponseException, ShopTokenException, ShopApiException, SQLAlchemyError) as e:
        msg = '{}: {}'.format(shop.name, e)
        print('error', msg)
    except ShopManualParsingException as e:
        print('error', msg)


def get_shop(shop_name):
    """Возвращаем магазин из списка всех магазинов
    доступных для ручного парсинга по его имени
    """
    for shop in manual_shops:
        if shop.name == shop_name:
            return shop
    else:
        msg = 'Магазин с названием: {}, отсутствует в списке доступных для парсинга магазинов'.format(
            shop_name)
        raise ShopManualParsingException(msg)


def shop_parser(shop):
    """Принимает объект магазина, запускает парсинг, сохраняет результат"""
    msg = 'парсинг магазина: {}'.format(shop.name)
    print(msg)
    try:
        parsing_results = shop.parsing()
        save_shops_data(parsing_results, shop.name)
    except (
            ShopBadResponseException, ShopTokenException, ShopApiException, SQLAlchemyError,
            Exception) as e:
        msg = '{}: {}'.format(shop.name, e)
        print('error', msg)


@click.command()
@click.option('--shops_list', '-l', is_flag=True, help='Вывести список доступных для парсинга магазинов')
@click.option('--one_shop', '-o', default=None, help='Запустить парсинг для одного выбранного магазина')
@click.option('--all_shops', '-a', default=None, help='Запустить парсинг для всех магазинов')
@click.option('--manual', '-p', nargs=2, default=None,
              help='Запустить парсинг в ручном режиме с указанием proxy')
def main(shops_list, one_shop, all_shops, manual):
    if shops_list:
        click.echo(shops)
    if one_shop:
        for shop in shops:
            if shop.name == one_shop:
                shop_parser(shop)
                break
        else:
            msg = 'нет доступного магазина с именем: {}'.format(one_shop)
            click.echo(msg)
    if all_shops:
        for shop in shops:
            shop_parser(shop)
    if manual:
        token, shop = manual
        manual_parsing(token, shop)


if __name__ == '__main__':
    main()
