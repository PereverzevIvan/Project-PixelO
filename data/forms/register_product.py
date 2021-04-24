# Форма для добавления товаров
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, StringField, SelectField, FieldList
from wtforms.validators import DataRequired


class RegisterProductForm(FlaskForm):
    name = StringField('Имя товара', validators=[DataRequired()])
    price = StringField('Цена товара', validators=[DataRequired()])
    category = SelectField('Категория товара', validators=[DataRequired()])
    brand = StringField('Брэнд товара', validators=[DataRequired()])
    parameters = FieldList(StringField(''), validators=[DataRequired()])
    image = FileField('Приложите фотографию')
    submit = SubmitField('Подтвердить')

    # Названия характеристик
    chars = []
    # Категория выбрана
    category_is_choice = False
    # Параметры показаны пользователю
    params_is_showed = False

    # Метод для получения кол-ва характеристик товара
    def get_len_params(self):
        return len(self.parameters)

    # Метод для удаления старых полей характеристик товара
    def clean_params(self):
        while len(self.parameters) != 0:
            del self.parameters.entries[0]
