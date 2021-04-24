# Форма для добавления отзыва
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, RadioField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class AddNewsForm(FlaskForm):
    score = RadioField('Оценка', default='1', choices=['1', '2', '3', '4', '5'], validators=[DataRequired()])
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    is_private = BooleanField('Приватный отзыв', default=False)
    submit = SubmitField('Оставить отзыв')
