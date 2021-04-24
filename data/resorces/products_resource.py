# Ресурсы для работы с товарами
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.models.product import Product
from data.models.categories import Category
from data.parsers.products_reqparse import parser


# Примечание:
# {'message': 'ERROR'} - Сообщение "Что-то пошло не так"
# {'message': 'SUCCESS'} - Сообщение "Все прошло успешно"


# Функция для проверки, существует ли желаемый товар
def errors_with_product(product_id):
    session = db_session.create_session()
    products = session.query(Product).get(product_id)
    if not products:
        return True
    return False


# Функция для проверки, существует ли желаемая категория
def errors_with_category(category_id):
    session = db_session.create_session()
    category = session.query(Category).get(category_id)
    if not category:
        return True
    return False


# Класс для работы с одним конкретным товаром
class ProductsResource(Resource):
    # Получение товара
    def get(self, product_id):
        if type(product_id) == str and not product_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_product(product_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        result = {}
        result['message'] = 'SUCCESS'
        result['product'] = product.to_dict(
            only=('id', 'name', 'category', 'brand',
                  'parameters', 'image_path', 'price'))
        result['news'] = [i.dict_params() for i in product.news]
        return jsonify(result)

    # Удаление товара
    def delete(self, product_id):
        if type(product_id) == str and not product_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_product(product_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        session.delete(product)
        session.commit()
        return jsonify({'message': 'SUCCESS'})


# Класс для работы со множеством товаров
class ProductsListResource(Resource):
    # Получение всх товаров
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        result = {}
        result['products'] = [
            item.to_dict(only=('id', 'name', 'category', 'brand',
                               'parameters', 'image_path', 'price')) for item in products]
        result['message'] = 'SUCCESS'
        return jsonify(result)

    # Добавление товара
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product()

        product.id = args['id']
        product.name = args['name']
        product.price = args['price']
        product.category = args['category']
        product.parameters = args['parameters']
        product.brand = args['brand']
        product.image_path = args['image_path']

        session.add(product)
        session.commit()
        return jsonify({'message': 'SUCCESS'})


# Класс для работы с товарами в какой-то конкретной категории
class ProductsInCategory(Resource):
    # Получение всех товаров в выбранной категории
    def get(self, category_id):
        if type(category_id) == str and not category_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_category(category_id):
            return jsonify({'message': 'ERROR'})
        category_id = int(category_id)
        session = db_session.create_session()
        products = session.query(Product).filter(Product.category == category_id).all()
        result = {}
        result['products'] = [
            item.to_dict(only=('id', 'name', 'category', 'brand',
                               'parameters', 'image_path', 'price')) for item in products]
        result['message'] = 'SUCCESS'
        return jsonify(result)
