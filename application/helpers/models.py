import datetime

from sqlalchemy import Column, Integer, String, Date, Index, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI

Base = declarative_base()


class ItemsShop(Base):
    """Таблица с данными которые удалось вытянуть c сайта"""
    __tablename__ = 'items_shop'

    id = Column(Integer, primary_key=True)
    parse_date = Column(Date, default=datetime.datetime.today, index=True)
    asin = Column(String)
    url = Column(String)
    name = Column(String)
    price = Column(String)
    size = Column(String)
    sections = Column(String)
    photos = Column(String)
    colors = Column(String)
    details = Column(String)


class AsinsAmazon(Base):
    __tablename__ = 'asins_amazon'

    id = Column(Integer, primary_key=True)
    asin = Column(String)


def connect_db(db_url=DATABASE_URI, echo=True):
    """Создает подключение к базе данных, возвращает объект сессии базы данных"""
    engine = create_engine(db_url, echo=echo)
    Session = sessionmaker(bind=engine)
    return Session(), engine
