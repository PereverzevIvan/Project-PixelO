# Модель отзыва о товаре
import datetime
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("products.id"))

    user = orm.relation('User')
    product = orm.relation('Product')

    # Метод, возвращающий атрибуты экземпляра в виде словаря
    def dict_params(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_date': self.created_date.date(),
            'score': self.score,
            'is_private': self.is_private,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'user_name': self.user.name,
            'product_name': self.product.name
        }
