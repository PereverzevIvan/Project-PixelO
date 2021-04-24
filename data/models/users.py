# Модель пользователя
import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase
from requests import post


# Класс пользователя
class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # Корзина пользователя
    basket = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False, default='')
    avatar_path = sqlalchemy.Column(sqlalchemy.String, nullable=True,
                                    default='img/no_foto.jpg')
    # Роль пользователя
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    news = orm.relation("News", back_populates='user')

    def __repr__(self):
        return f'<{self.role}> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    # Метод для получения кол-ва товаров в корзине пользователя
    def len_basket(self):
        return len(self.basket.split(', '))
