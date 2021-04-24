# Парсер для ресурсов пользователей
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)
parser.add_argument('role', required=False)
parser.add_argument('avatar_path', required=False)
