# Yatube
Социальная сеть для публикации блогов.

Разработан по MVT архитектуре.Используется пагинация постов и кэширование. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Используется пагинация постов и кеширование. Написаны тесты, проверяющие работу сервиса.

# Стэк технологий
* Python 3.8
* Django 2.2
* SQLite3
* unitest
* pytest

# Установка 

Клонируйте репозиторий:  

    https://github.com/dafun34/hw05_final.git
Создайте виртуальное окружение:  

    python -m venv venv

Активируйте виртуальное окружение:  

    . venv/Scripts/activate
Установите необходимые зависимости:  

    pip install -r requirements.txt

Создайте миграции:  

    python manage.py makemigrations

Примените миграции:

    python manage.py migrate

Соберите статику:

    python manage.py collectstatic

Создайте суперпользователя:

    python manage.py createsuperuser

Запускайте сервер:

    python manage.py runserver

Теперь ваш сервер доступен на: 

    http://127.0.0.1:8000/
    
После создания суперпользователя и запуска сервера, вам будет доступна админка, из которой можно управлять проектом, добавлять и удалять группы, посты, пользователей и т.д. по адресу: 

    127.0.0.1:8000/admin/

# Тесты 
Тесты запускаются командой:

    pytest
    
