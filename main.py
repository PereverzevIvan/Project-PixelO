# Проводим импорт всех нужных библиотек и модулей
from flask import Flask, request, render_template, redirect
from flask_restful import Api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from requests import post, get, delete

# Проводим импорт форм для отправки данных html-страницы на сервер
from data.forms.login import LoginForm
from data.forms.register import RegisterForm
from data.forms.register_product import RegisterProductForm
from data.forms.register_category import RegisterCategoryForm
from data.forms.add_news import AddNewsForm

from data import db_session
from data.models.users import User

# Импортируем ресурсы для работы с юзерами, товарами, категориями и т. д.
from data.resorces import products_resource, users_resource, categories_resource, news_resource

# Константы для более удобного доступа к ресурсам
PRODUCTS_API = 'http://localhost:5000/api/v2/products'
CATEGORIES_API = 'http://localhost:5000/api/v2/categories'
USERS_API = 'http://localhost:5000/api/v2/users'
PRODUCTS_IN_CATEGORY_API = 'http://localhost:5000/api/v2/products_in_category/'
NEWS_API = 'http://localhost:5000/api/v2/news'
BASKET_API = 'http://localhost:5000/api/v2/basket'

# Переменные для отображения оповещений на страницах
product_profile_message = {'corr': '', 'error': ''}
user_profile_message = {'corr': '', 'error': ''}

# Текущая категория при добавлении товара
current_category = ''

# Создаем приложение Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

# Подключаем все ресурсы
api.add_resource(users_resource.UsersListResource, '/api/v2/users')
api.add_resource(users_resource.UsersResource, '/api/v2/users/<user_id>')
api.add_resource(users_resource.BasketResource, '/api/v2/basket/<user_id>/<product_id>')

api.add_resource(products_resource.ProductsListResource, '/api/v2/products')
api.add_resource(products_resource.ProductsResource, '/api/v2/products/<product_id>')
api.add_resource(products_resource.ProductsInCategory, '/api/v2/products_in_category/<category_id>')

api.add_resource(categories_resource.CategoriesListResource, '/api/v2/categories')
api.add_resource(categories_resource.CategoriesResource, '/api/v2/categories/<category_id>')

api.add_resource(news_resource.NewsListResource, '/api/v2/news')
api.add_resource(news_resource.NewsResource, '/api/v2/news/<int:news_id>')

# Проводим настройки для возможности авторизации и выхода пользователей
login_manager = LoginManager()
login_manager.init_app(app)


# Декоратор для глобальной авторизации пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Декоратор для дисконекта пользователя с системой
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Декоратор главной страницы
@app.route('/', methods=['GET'])
def index():
    categories = get(CATEGORIES_API).json()['categories']
    return render_template('category_list.html', categories=categories)


# Декоратор для регистрации пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Форма регистрации
    form = RegisterForm()
    # Если все поля заполнены
    if form.validate_on_submit():
        # Переменная, означающая, что пользователь может быть зарегистрирован
        can_register = True
        # Получаем список всех пользователей
        users = get(USERS_API).json()['users']
        # Вычисляем id нового пользователя
        id_ = max([i['id'] for i in users]) + 1 if users else 1
        role = 'admin' if id_ == 1 else 'user'
        # Создаем словарь параметров для регистрации пользователя
        params = {'id': id_, 'email': form.email.data, 'password': form.password_again.data,
                  'name': form.name.data, 'role': role}
        # Проверка совпадения паролей
        if form.password.data != form.password_again.data:
            mes = 'Пароли не совпадают'
            can_register = False
        # Проверка уникальности эл. почты
        elif params['email'] in [i['email'] for i in users]:
            mes = 'Данный адрес электронной почты уже занят'
            can_register = False
        # Проверка уникальности имени пользователя
        elif params['name'] in [i['name'] for i in users]:
            mes = 'Это имя уже используется'
            can_register = False
        if can_register:
            # Добавление пользователя в базу
            file = form.image.data
            # Если он вообще прикреплен
            if file is not None:
                # Создаем путь по которому будем хранить файл
                path = f'img/users/{params["name"]}.jpg'
                # Добавляем путь к файлу в параметры товара
                params['avatar_path'] = path
            # Добавляем товар в бд
            result = post(USERS_API, json=params).json()
            if result['message'] == 'SUCCESS':
                path = params.get('avatar_path', None)
                if path is not None:
                    file.save('static/' + path)
                return redirect("/login")
        else:
            # Рендер шаблона для отображения ошибки
            return render_template('register.html', form=form, message=mes, title="Регистрация")
    # Рендер шаблона
    return render_template('register.html', form=form, title='Регистрация')


# Декоратор для авторизации пользователя через форму
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Форма авторизации
    form = LoginForm()
    # Если все поля заполнены
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            user = db_sess.query(User).filter(User.name == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


# Декоратор для регистрации категорий товаров
@app.route('/register_category', methods=['GET', 'POST'])
def register_category():
    # Проверка, евляется ли текущий пользователь администратором
    if current_user.is_anonymous or current_user.role != 'admin':
        return redirect('/not_found')
    # Форма регистрации категории
    form = RegisterCategoryForm()
    # Для более быстрого доступа ко всем котегориям в бд
    # Если все поля заполнены
    if form.validate_on_submit():
        # Получаем все категории из бд
        categories = get(CATEGORIES_API).json()
        # Вычисляем id для будущей категории
        id_ = max([i['id'] for i in categories['categories']]) + 1 if categories['categories'] else 1
        # Параметры для будущей категории
        params = {'id': id_, 'name': form.name.data, 'parameters': form.parameters.data}
        # Получем прикрепленный файл
        file = form.image.data
        # Создаем путь по которому будем хранить файл
        path = f'img/categories/{params["name"]}.jpg'
        # Добавляем путь к файлу в параметры товара
        params['image_path'] = path
        # Добавление категории в бд
        result = post(CATEGORIES_API, json=params).json()
        if result['message'] == 'SUCCESS':
            # Сохраняем файл
            file.save('static/' + path)
            return render_template('register_category.html', form=form, message_corr='Категория была успешно добавлена')
        else:
            return render_template('register_category.html', form=form, message='Добавление категории не удалось')
    # Рендер шаблона формы для регистрации категорий
    return render_template('register_category.html', form=form)


# Декоратор для регистрации товаров
@app.route('/register_product', methods=['GET', 'POST'])
def register_product():
    global current_category
    # Проверка, евляется ли текущий пользователь администратором
    if current_user.is_anonymous or current_user.role != 'admin':
        return redirect('/not_found')
    # Форма для регистрации товара
    form = RegisterProductForm()
    # Получаем все категории
    categories = get(CATEGORIES_API).json()
    # Получаем все имена категорий
    cat_names = [i['name'] for i in categories['categories']]
    # Устанавливаем значения выпадающего списка
    form.category.choices = ['', *cat_names]
    # По умолчанию устанавливаем пустую категорию товара
    form.category.data = '' if form.category.data is None else form.category.data
    # Переменная для отображение полей с характеристиками товара
    form.params_is_showed = False if len(form.parameters) == 0 else True
    # Проверяем, указана ли категория товара
    form.category_is_choice = False if form.category.data == '' else True
    if form.category_is_choice:
        # Если категория выбрана и она не совпадает с текущей
        if current_category != form.category.data:
            # Меняем текущую категорию
            current_category = form.category.data
            # Указываем, что поля с характеристиками товара не были показаны пользователю
            form.params_is_showed = False
            # Удаляем существующие поля характеристик товара
            form.clean_params()
        # Узнаем имена характеристик товаров данной категории
        product_chars = [i for i in get(CATEGORIES_API + f'/{cat_names.index(form.data["category"]) + 1}'
                                                         f'').json()['categories']['parameters'].split(', ')]
        # Создаем нужное кол-во полей для ввода
        if form.get_len_params() != len(product_chars):
            [form.parameters.append_entry() for i in product_chars]
        # Сохраняем названия характеристик
        form.chars = product_chars
    if request.method == 'POST':
        # Если не выбрана категория товара
        if not form.category_is_choice:
            mes = 'Категория не выбрана'
            return render_template('register_product.html', form=form, cat_names=cat_names, message=mes)
        else:
            # Получаем содержимое всех полей
            content = [i.data for i in form.parameters]
            # Если есть хоть одно не заполненное поле
            if not all(content):
                # Если характеристика товаров данной категории не были показаны пользователю
                if not form.params_is_showed:
                    return render_template('register_product.html', form=form, cat_names=cat_names)
                else:
                    mes = 'Поля характеристик товара не заполнены'
                    return render_template('register_product.html', form=form, cat_names=cat_names, message=mes)
        if form.validate_on_submit():
            # Получаем все товары
            products = get(PRODUCTS_API).json()
            # Вычисляем id для будующего товара
            id_ = max([i['id'] for i in products['products']]) + 1 if products['products'] else 1
            # Параметры для будущего товара
            params = {'id': id_, 'name': form.name.data, 'category': cat_names.index(form.category.data) + 1,
                      'brand': form.brand.data, 'price': form.price.data}
            chars = ', '.join([f'{form.chars[i]} - {form.parameters[i].data}' for i in range(len(form.chars))])
            params['parameters'] = chars
            # Получем прикрепленный файл
            file = form.image.data
            # Если он вообще прикреплен
            if file is not None:
                # Создаем путь по которому будем хранить файл
                path = f'img/products/{params["name"]}.jpg'
                # Добавляем путь к файлу в параметры товара
                params['image_path'] = path
                # Добавляем товар в бд
                result = post(PRODUCTS_API, json=params).json()
                if result['message'] == 'SUCCESS':
                    # Сохраняем файл
                    file.save('static/' + path)
                    mes = 'Товар успешно добавлен'
                    return render_template('register_product.html', form=form, cat_names=cat_names, message_corr=mes)
            else:
                mes = 'Прикрепите изображение'
                return render_template('register_product.html', form=form, cat_names=cat_names, message=mes)
    return render_template('register_product.html', form=form, cat_names=cat_names)


# Декоратор страницы профиля пользователя
@app.route('/user_profile/<user_id>')
def user_profile(user_id):
    global user_profile_message
    # Пытаемся найти нужного пользователя
    user = get(USERS_API + f'/{user_id}').json()
    # Переменна, говорящая, нужно ли отобразить корзину пользователя
    basket_need = False
    # Если не получилось, переходим на страницу "Ничего не найдено"
    if user['message'] == 'ERROR':
        return redirect('/not_found')
    # Если текущий пользователь не анонимный и его id совпадает с id юзера, профиль которого мы хотим открыть
    if not current_user.is_anonymous and current_user.id == int(user_id):
        # Получаем корзину пользователя
        basket = get(BASKET_API + f'/{current_user.id}/1').json()
        if basket['message'] == 'SUCCESS':
            basket_need = True
    # Сообщения, отображаемые на странице
    corr_mes = user_profile_message['corr']
    error_mes = user_profile_message['error']

    user_profile_message['corr'] = user_profile_message['error'] = ''
    # Если нужно вывести корзину
    if basket_need:
        return render_template('user_profile.html', user=user['user'], news=user['news'],
                               basket=basket['products'], finish_price=basket['finish_price'],
                               message_corr=corr_mes, message_error=error_mes)
    else:
        return render_template('user_profile.html', user=user['user'], news=user['news'],
                               message_corr=corr_mes, message_error=error_mes)


# Декоратор страницы "Ничего не найдено"
@app.route('/not_found')
def not_found():
    mes = ['Страница не найдена или удалена', 'Возможно, если вы авторизируетесь, что-то изменится']
    return render_template('not_found_page.html', message=mes)


# Декоратор страницы со всеми товарами в выбранной категории
@app.route('/products_in_category/<category_id>')
def products_in_category(category_id):
    # Получаем все категории
    products = get(PRODUCTS_IN_CATEGORY_API + category_id).json()
    if products['message'] == 'ERROR':
        return redirect('/not_found')
    if products['message'] == 'SUCCESS':
        return render_template('products_in_category.html', products=products['products'])


# Декоратор страницы профиля товара
@app.route('/product_profile/<product_id>', methods=['GET', 'POST'])
def product_profile(product_id):
    global product_profile_message
    # Получаем товар
    product = get(PRODUCTS_API + f'/{product_id}').json()
    if product['message'] == 'ERROR':
        return redirect('/not_found')
    # Если успешно
    if product['message'] == 'SUCCESS':
        # Получаем отзывы, оставленные к этому товару
        news = product['news']
        product = product['product']
        # Его характеристики
        params = [i.split(' - ') for i in product['parameters'].split(', ')]
        # Форма добавления отзыва
        form = AddNewsForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Получаем все отзывы
                news_in_db = get(NEWS_API).json()
                # Рассчитываем id для нового отзыва
                id_ = max([i['id'] for i in news_in_db['news']]) + 1 if news_in_db['news'] else 1
                # Параметры для создания нового отзыва
                params_for_post = {'title': form.title.data, 'id': id_, 'content': form.content.data,
                                   'score': form.score.data,
                                   'user_id': current_user.id,
                                   'product_id': product['id']}

                result = post(NEWS_API, json=params_for_post).json()
                if result['message'] == 'SUCCESS':
                    return redirect(f"/product_profile/{product['id']}")
        # Все оценки товара
        all_score = [int(i['score']) for i in news]
        # Средняя оценка товара
        score_average = sum(all_score) / len(all_score) if len(all_score) >= 1 else 0
        corr_mes = product_profile_message['corr']
        error_mes = product_profile_message['error']
        product_profile_message['corr'] = product_profile_message['error'] = ''
    return render_template('product_profile.html', product=product, params=params, news=news,
                           form=form, score_average=score_average, message_corr=corr_mes, message_error=error_mes)


# Декоратор страницы покупки товара
@app.route('/buy_product')
def buy_product():
    text = 'Увы, вы пока не можете совершить покупку'
    return render_template('buy_product.html', message=text)


# Декоратор для произведения каких-либо действий над комментарием
@app.route('/to_do_news/<action>/<news_id>/<product_id>', methods=['GET', 'POST', 'DELETE'])
def to_do_news(action, news_id, product_id):
    if action == 'delete':
        delete(NEWS_API + f'/{news_id}')
    elif action == 'edit':
        pass
    return redirect(f'/product_profile/{product_id}')


# Декоратор для добавления товара в корзину
@app.route('/add_product_in_basket/<product_id>', methods=['GET', 'POST'])
def add_product_in_basket(product_id):
    global product_profile_message
    # Если пользователь не анонимный
    if not current_user.is_anonymous:
        result = post(f'http://localhost:5000/api/v2/basket/{current_user.id}/{product_id}').json()
        if result['message'] == 'SUCCESS':
            product_profile_message['corr'] = 'Товар успешно добавлен в корзину'
        if result['message'] == 'ERROR':
            product_profile_message['error'] = 'Товар уже добавлен в корзину'
    else:
        product_profile_message['error'] = 'Только авторизированные пользователи могут добавлять товар в корзину'
    return redirect(f'/product_profile/{product_id}')


# Декоратор для удаления товара из корзины
@app.route('/delete_product_from_basket/<user_id>/<product_id>', methods=['GET', 'POST', 'DELETE'])
def delete_product_from_basket(user_id, product_id):
    global user_profile_message
    result = delete(f'http://localhost:5000/api/v2/basket/{current_user.id}/{product_id}').json()
    if result['message'] == 'SUCCESS':
        user_profile_message['corr'] = 'Товар был успешно удален из корзины'
    if result['message'] == 'ERROR':
        user_profile_message['error'] = 'Не удалось удалить товар из корзины'
    return redirect(f'/user_profile/{user_id}')


# Декоратор страницы для редактирования профиля пользователя
@app.route('/edit_user_profile/<user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    # Форма регистрации пользователя
    form = RegisterForm()
    user = get(USERS_API + f'/{user_id}').json()
    if user['message'] == 'ERROR':
        return redirect('/not_found')
    else:
        user = user['user']
        form.name.render_kw = {"placeholder": user['name']}
        form.email.render_kw = {"placeholder": user['email']}
    if form.validate_on_submit():
        # Переменная, означающая, что пользователь может быть зарегистрирован
        can_register = True
        # Получаем список всех пользователей
        users = get(USERS_API).json()['users']
        # Создаем словарь параметров для регистрации пользователя
        params = {'email': form.email.data, 'password': form.password_again.data,
                  'name': form.name.data}
        # Проверка совпадения паролей
        if form.password.data != form.password_again.data:
            mes = 'Пароли не совпадают'
            can_register = False
        # Проверка уникальности эл. почты
        elif params['email'] in [i['email'] for i in users]:
            mes = 'Данный адрес электронной почты уже занят'
            can_register = False
        # Проверка уникальности имени пользователя
        elif params['name'] in [i['name'] for i in users]:
            mes = 'Это имя уже используется'
            can_register = False
        if can_register:
            # Добавление пользователя в базу
            file = form.image.data
            # Если он вообще прикреплен
            if file is not None:
                # Создаем путь по которому будем хранить файл
                path = f'img/users/{params["name"]}.jpg'
                # Добавляем путь к файлу в параметры товара
                params['avatar_path'] = path
            # Добавляем товар в бд
            result = post(USERS_API + f'/{user_id}', json=params).json()
            if result['message'] == 'SUCCESS':
                path = params.get('avatar_path', None)
                if path is not None:
                    file.save('static/' + path)
                return redirect(f"/user_profile/{user_id}")
        else:
            # Рендер шаблона для отображения ошибки
            return render_template('register.html', form=form, message=mes, title="Редактирование профиля")
    # Рендер шаблона
    return render_template('register.html', form=form, title="Редактирование профиля")


if __name__ == '__main__':
    # Инициализируем бд в нашей программе
    db_session.global_init("db/data_base.db")
    app.run()
