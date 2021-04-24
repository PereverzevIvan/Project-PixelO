# Парсер для ресурсов отзывов
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('product_id', required=True, type=int)
parser.add_argument('score', required=True, type=int)
