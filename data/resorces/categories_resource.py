# Ресурсы для работы с категориями
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.models.categories import Category
from data.parsers.categories_reqparse import parser


# Примечание:
# {'message': 'ERROR'} - Сообщение "Что-то пошло не так"
# {'message': 'SUCCESS'} - Сообщение "Все прошло успешно"

# Функция для проверки, существует ли желаемая категория
def errors_with_category(category_id):
    session = db_session.create_session()
    category = session.query(Category).get(category_id)
    if not category:
        return True
    return False


# Класс для работы с одной конкретной категорией
class CategoriesResource(Resource):
    # Получение категории
    def get(self, category_id):
        if type(category_id) == str and not category_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_category(category_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        category = session.query(Category).get(category_id)
        result = {}
        result['categories'] = category.to_dict(only=('id', 'name', 'parameters', 'image_path'))
        result['message'] = 'SUCCESS'
        return jsonify(result)

    # Удаление категории
    def delete(self, category_id):
        if type(category_id) == str and not category_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_category(category_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        category = session.query(Category).get(category_id)
        session.delete(category)
        session.commit()
        return jsonify({'message': 'SUCCESS'})


# Класс для работы со множеством категорий
class CategoriesListResource(Resource):
    # Получаем все категории
    def get(self):
        session = db_session.create_session()
        categories = session.query(Category).all()
        result = {}
        result['categories'] = [item.to_dict(
            only=('id', 'name', 'parameters', 'image_path')) for item in categories]
        result['message'] = 'SUCCESS'
        return jsonify(result)

    # Добавляем категорию
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        category = Category()

        category.id = args['id']
        category.name = args['name']
        category.parameters = args['parameters']
        category.image_path = args['image_path']

        session.add(category)
        session.commit()
        return jsonify({'message': 'SUCCESS'})
