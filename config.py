"""
Настройки парсера: конфигурация базы данных
конфигурации магазинов.
"""
import os
import yaml

with open('./app.conf') as f:
    SHOPS_SETTINGS = yaml.load(f, Loader=yaml.FullLoader)

# настройки базы данных
DATABASE_URI = os.environ.get('DATABASE_URI', SHOPS_SETTINGS['db']['url'])

