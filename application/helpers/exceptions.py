class ShopBadResponseException(Exception):
    """Ошибка доступа или сайт не доступен"""
    pass


class ShopBanException(Exception):
    """Ошибка доступа, amazon блокирует работу парсера"""
    pass


class ShopAuthException(Exception):
    """Ошибка авторизации"""
    pass


class ShopTokenException(Exception):
    """Ошибка получения токена для доступа к API amazon"""
    pass


class ShopApiException(Exception):
    """Ошибка API магазина, изменение api"""
    pass


class ShopManualParsingException(Exception):
    """Ошибка возникающая при ручном парсинге магазина"""
    pass


class GeoCoderException(Exception):
    """Ошибка уточнения адреса в стороннем API"""
    pass


class ShortLinkDirectoryException(Exception):
    """Ошибка генерации коротких url"""
    pass


class ParsingDirectoryException(Exception):
    """Ошибка генерации справочников"""
    pass


class ParsingPublishDirectoryException(Exception):
    """Ошибка публикации справочников"""
    pass
