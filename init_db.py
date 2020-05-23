import secrets

from passlib.hash import sha256_crypt
from sqlalchemy import MetaData, create_engine

from shop.db import (Gender, order_product_table, order_table,
                     product_table, token_table, user_order_table, user_table)
from shop.settings import config

DSN = 'postgresql://{user}:{password}@{host}:{port}/{database}'


def create_tables(engine):
    meta = MetaData()
    tables = [
        user_table, token_table, product_table,
        order_table, order_product_table, user_order_table
    ]
    meta.create_all(bind=engine, tables=tables)


def insert_users(conn):
    conn.execute(user_table.insert(), [{
        'login': 'admin',
        'password': sha256_crypt.hash('admin'),
        'first_name': 'Ivan',
        'surname': 'Ivanov',
        'middle_name': 'Ivanovich',
        'sex': Gender.male,
        'age': 25
    }, {
        'login': 'user1',
        'password': sha256_crypt.hash('user1'),
        'first_name': 'Petr',
        'surname': 'Petrov',
        'middle_name': 'Petrovich',
        'sex': Gender.male,
        'age': 26
    }])


def insert_tokens(conn):
    tokens = []
    users = conn.execute(user_table.select())
    for user in users:
        tokens.append({
            'user_id': user.id,
            'token': secrets.token_hex(32)
        })

    conn.execute(token_table.insert(), tokens)


def insert_products(conn):
    conn.execute(product_table.insert(), [{
        'name': 'Chocolate',
        'description': 'Delicious chocolate',
        'price': 2.5,
        'left_in_stock': 10
    }, {
        'name': 'Juice',
        'description': 'Fruit juice',
        'price': 1.3,
        'left_in_stock': 17
    }, {
        'name': 'Gamburger',
        'description': 'Very tasty gamburger...',
        'price': 4.2,
        'left_in_stock': 3
    }])


def seed_db(engine):
    with engine.connect() as conn:
        insert_users(conn)
        insert_tokens(conn)
        insert_products(conn)


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    db_engine = create_engine(db_url)

    create_tables(db_engine)
    seed_db(db_engine)
