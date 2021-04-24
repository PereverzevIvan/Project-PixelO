# Ресурсы для работы с пользователями
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.models.users import User
from data.models.product import Product
from data.parsers.users_reqparse import parser


# Примечание:
# {'message': 'ERROR'} - Сообщение "Что-то пошло не так"
# {'message': 'SUCCESS'} - Сообщение "Все прошло успешно"


# Функция для проверки, существует ли желаемый пользователь
def errors_with_users(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        return True
    return False


# Функция для проверки, существует ли желаемый товар
def errors_with_product(product_id):
    session = db_session.create_session()
    products = session.query(Product).get(product_id)
    if not products:
        return True
    return False


# Класс для работы с одним конкретным пользователем
class UsersResource(Resource):
    # Получение пользователя
    def get(self, user_id):
        if type(user_id) == str and not user_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_users(user_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        result = {}
        result['user'] = user.to_dict(
            only=('id', 'name', 'email',
                  'hashed_password', 'role', 'avatar_path', 'modified_date', 'basket'))
        result['message'] = 'SUCCESS'
        result['news'] = [i.dict_params() for i in user.news]
        return jsonify(result)

    # Удаление удаление пользователя
    def delete(self, user_id):
        if type(user_id) == str and not user_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_users(user_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'message': 'SUCCESS'})

    # Изменение информации об уже существующем пользователе
    def post(self, user_id):
        if type(user_id) == str and not user_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_users(user_id):
            return jsonify({'message': 'ERROR'})
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        user.name = args['name']
        user.email = args['email']
        if args['avatar_path'] is not None:
            user.avatar_path = args['avatar_path']
        user.set_password(args['password'])

        session.commit()
        return jsonify({'message': 'SUCCESS'})


# Класс для работы со множеством пользователей
class UsersListResource(Resource):
    # Получение всех пользователей
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        result = {}
        result['users'] = [
            item.to_dict(only=('id', 'name', 'email',
                               'hashed_password', 'role', 'avatar_path', 'modified_date', 'basket'))
            for item in users]
        result['message'] = 'SUCCESS'
        return jsonify(result)

    # Добавление пользоветеля
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User()

        user.id = args['id']
        user.name = args['name']
        user.email = args['email']
        user.role = args['role']
        user.avatar_path = args['avatar_path']
        user.set_password(args['password'])

        session.add(user)
        session.commit()
        return jsonify({'message': 'SUCCESS'})


# Класс для работы с корзиной пользовател
class BasketResource(Resource):
    # Удаление товара из корзины
    def delete(self, user_id, product_id):
        if type(user_id) == str and not user_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_users(user_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        basket = session.query(User).get(user_id).basket
        basket = basket.split(', ') if basket is not None else []
        if str(product_id) in basket:
            del basket[basket.index(f'{product_id}')]
            basket = ', '.join(basket) if len(basket) >= 1 else None
            session.query(User).get(user_id).basket = basket
            session.commit()
            return jsonify({'message': 'SUCCESS'})
        return jsonify({'message': 'ERROR'})

    # Получение товаров в корзине
    def get(self, user_id, product_id):
        if type(user_id) == str and not user_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_users(user_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        products = session.query(Product).all()
        basket = session.query(User).get(user_id)
        basket = basket.basket.split(', ')
        result = {}
        result['products'] = [
            {'id': i.id, 'name': i.name, 'image_path': i.image_path, 'price': i.price}
            for i in products if str(i.id) in basket]
        result['message'] = 'SUCCESS'
        result['finish_price'] = sum([int(i['price']) for i in result['products']])
        return jsonify(result)

    # Добавление товара в корзину
    def post(self, user_id, product_id):
        if type(user_id) == str and not user_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_users(user_id):
            return jsonify({'message': 'ERROR'})
        if type(product_id) == str and not product_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_product(product_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        basket = session.query(User).get(user_id).basket
        basket = basket.split(', ') if basket is not None else []
        if str(product_id) not in basket:
            basket.append(f'{product_id}')
            basket = ', '.join(basket) if len(basket) >= 1 else str(product_id)
            session.query(User).get(user_id).basket = basket
            session.commit()
            return jsonify({'message': 'SUCCESS'})
        return jsonify({'message': 'ERROR'})
