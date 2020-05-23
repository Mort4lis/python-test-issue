import enum
import uuid

from aiopg.sa import create_engine
from sqlalchemy import (Column, Enum, ForeignKey, Integer, MetaData, Numeric, String, Table, Text)
from sqlalchemy.dialects.postgresql import UUID

meta = MetaData()


class Gender(enum.Enum):
    """Перечисление (Enum) полов."""

    male = 'Мужской'
    female = 'Женский'


user_table = Table(
    'users', meta,

    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    Column('login', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    Column('first_name', String(255), nullable=False),
    Column('surname', String(255), nullable=False),
    Column('middle_name', String(255), nullable=True),
    Column('sex', Enum(Gender)),
    Column('age', Integer, nullable=False)
)

token_table = Table(
    'tokens', meta,

    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    Column('token', String(64), unique=True, nullable=False),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'))
)

user_order_table = Table(
    'users_orders', meta,

    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('order_id', UUID(as_uuid=True), ForeignKey('orders.id')),
)

order_table = Table(
    'orders', meta,

    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    Column('number', Integer, nullable=False)
)

order_product_table = Table(
    'orders_products', meta,

    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id')),
    Column('order_id', UUID(as_uuid=True), ForeignKey('orders.id')),
    Column('quantity', Integer, nullable=False)
)

product_table = Table(
    'products', meta,

    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    Column('name', String(255), nullable=False),
    Column('description', Text, nullable=False),
    Column('slug', String(255), unique=True, nullable=False),
    Column('price', Numeric, nullable=False),
    Column('left_in_stock', Integer, nullable=False)
)


async def init_pg(app):
    """Инициализация объекта engine БД."""
    config = app['config']['postgres']
    engine = await create_engine(**config)
    app['db'] = engine


async def close_pg(app):
    """Завершение всех соединенией с БД."""
    app['db'].close()
    await app['db'].wait_closed()
