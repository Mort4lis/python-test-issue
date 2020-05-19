from sqlalchemy import MetaData, create_engine

from shop.db import order, order_product, product, user, user_order
from shop.settings import config

DSN = 'postgresql://{user}:{password}@{host}:{port}/{database}'


def create_tables(engine):
    meta = MetaData()
    tables = [user, product, order, order_product, user_order]
    meta.create_all(bind=engine, tables=tables)


def sample_data(engine):
    pass


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
