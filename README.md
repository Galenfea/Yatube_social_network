# Yatube_social_network

Социальная сеть:
- регистрация пользователей;
- блоги;
- подписка/отписка на чужие блоги;
- комментарии под постами;
- сообщества, объединяющие тематические посты из личных блогов.

## Автор:
- Отаров Александр (galenfea@gmail.com)

## Применяемые технологии:

- Django 2,2,16
- SQLite 3
- sorl-thumbnail 12.7.0

## Как запустить проект:

_Клонировать репозиторий и перейти в него в командной строке:_
```
git clone https://github.com/Galenfea/Yatube_social_network.git
cd yatube_social_network
```

_Cоздать и активировать виртуальное окружение:_
```
python -m venv venv
source venv/Scripts/activate
```

_Установить зависимости из файла requirements.txt:_
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

_Выполнить миграции и запустить проект:_
```
cd yatube_social_network
python manage.py migrate
python manage.py runserver
```
