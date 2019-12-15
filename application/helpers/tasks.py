from application.helpers import exceptions as exc
from application.helpers.shops import shops_cls
from parser import shop_parser


def automatic_parsing_task():
    """Автоматический парсинг магазинов"""
    for shop_cls in shops_cls:
        try:
            shop = shop_cls()
            shop_parser(shop)
        except (
                exc.ShopBadResponseException, exc.ShopTokenException, exc.ShopApiException,
                Exception) as e:
            msg = 'ошибка автоматического парсинга: {}: {}'.format(shop.name, e)
            print('error', msg)
