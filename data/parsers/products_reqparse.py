# Парсер для ресурсов товаров
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('price', required=True)
parser.add_argument('name', required=True)
parser.add_argument('category', required=True, type=int)
parser.add_argument('brand', required=True)
parser.add_argument('parameters', required=True)
parser.add_argument('image_path', required=True)
