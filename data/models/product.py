# Модель товара
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс товара
class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    category = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))
    brand = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("brands.id"))
    parameters = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='static/img/products/no_foto.jpg')
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    news = orm.relation("News", back_populates='product')
