# Форма для регистрации пользователей
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField
from flask_wtf.file import FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Адрес эл. почты', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Логин', validators=[DataRequired()])
    image = FileField('Приложите фотографию')
    remember_me = BooleanField('Запомнить меня', default=False)
    submit = SubmitField('Подтвердить')
