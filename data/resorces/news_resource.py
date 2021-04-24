# Ресурсы для работы с отзывами
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.models.news import News
from data.parsers.news_reqparse import parser


# Примечание:
# {'message': 'ERROR'} - Сообщение "Что-то пошло не так"
# {'message': 'SUCCESS'} - Сообщение "Все прошло успешно"


# Функция для проверки, существует ли желаемый отзыв
def errors_with_news(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        return True
    return False


# Класс для работы с одним конкретным отзывом
class NewsResource(Resource):
    # Получение отзыва
    def get(self, news_id):
        if type(news_id) == str and not news_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_news(news_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        result = {}
        result['message'] = 'SUCCESS'
        result['news'] = news.to_dict(
            only=('id', 'title', 'content', 'is_private', 'created_date', 'score'))
        return jsonify(result)

    # Удаление отзыва
    def delete(self, news_id):
        if type(news_id) == str and not news_id.isdigit():
            return jsonify({'message': 'ERROR'})
        if errors_with_news(news_id):
            return jsonify({'message': 'ERROR'})
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'message': 'SUCCESS'})


# Класс для работы со множеством отзывов
class NewsListResource(Resource):
    # Получение всех отзывов
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()

        result = {}
        result['news'] = [item.to_dict(
            only=('id', 'title', 'content', 'is_private', 'created_date', 'score')) for item in news]
        result['message'] = 'SUCCESS'
        return jsonify(result)

    # Добавление отзыва
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = News()

        news.id = args['id']
        news.title = args['title']
        news.content = args['content']
        news.user_id = args['user_id']
        news.product_id = args['product_id']
        news.score = args['score']

        session.add(news)
        session.commit()
        return jsonify({'message': 'SUCCESS'})
