# Модель брэнда товара
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Brand(SqlAlchemyBase):
    __tablename__ = 'brands'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
