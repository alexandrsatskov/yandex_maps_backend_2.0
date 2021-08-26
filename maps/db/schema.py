from geoalchemy2 import Geometry
from sqlalchemy import (
    Table, MetaData, Column, column,
    Integer, String, Text, BigInteger,
    ForeignKey,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.sql.expression import and_

# SQLAlchemy рекомендует использовать единый формат для генерации названий для
# индексов и внешних ключей.
# https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        col.name for col in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)

users_table = Table(
    'users',
    metadata,
    Column('user_email', String, primary_key=True)
)

places_table = Table(
    'places',
    metadata,
    Column('place_uid', String, primary_key=True),
    Column('place_id', BigInteger, nullable=False),
    Column('place_title', String, nullable=True, default=''),
    Column('coordinates', Geometry(
        geometry_type='POINT', srid=4326, nullable=False)
    )
)

user_places_table = Table(
    'user_places',
    metadata,
    Column('user_email', ForeignKey('users.user_email'), primary_key=True),
    Column('place_uid', ForeignKey('places.place_uid'), primary_key=True)
)

user_feedbacks_table = Table(
    'user_feedbacks',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_email', String, ForeignKey('users.user_email'), nullable=False),
    Column('place_uid', String, ForeignKey('places.place_uid'), nullable=False),
    Column('feedback_rate', Integer, nullable=False, default=0),
    Column('feedback_text', Text, nullable=False, default=''),
    # Пришлось создавать общий констрейнт на два поля,
    # вместо констрейнта на каждое, потому что в ином случае
    # не работает on_conflict_do_update() -> [POST] /user_places
    UniqueConstraint('user_email', 'place_uid', name=''),
    CheckConstraint(
        and_(column('feedback_rate') >= 0, column('feedback_rate') <= 5),
        name='feedback_rate'
    )
)
