# Форма для добавления категорий
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextField, FileField
from wtforms.validators import DataRequired


class RegisterCategoryForm(FlaskForm):
    name = StringField('Имя категории', validators=[DataRequired()])
    parameters = TextField('Характеристики товаров этой категории', validators=[DataRequired()])
    image = FileField('Приложите фотографию', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
