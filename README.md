[![Foodgram workflow](https://github.com/Aykes-Dev/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Aykes-Dev/foodgram-project-react/actions/workflows/main.yml)
# Foodgram
###
Foodgram – инновационный веб-ресурс для публикации кулинарных рецептов. Это не просто сайт, это целое сообщество единомышленников, где каждый может поделиться своими уникальными кулинарными идеями и открытиями. Наша миссия - делать процесс приготовления пищи доступным, интересным и вдохновляющим для всех, независимо от уровня кулинарного мастерства.

![logo](image_for_git.jpg)



## Технологии
#### 1. Frontend:
- Node.js
- Next.js
- React

\* Полный список библиотек в файле packeje.json

#### 2. Backend:
- Django
- DRF
- Gunicorn

\* Полный список библиотек в файле requirements.txt

#### 3. Сервер:
nginx

#### 4. Деплой
- Docker
- Docker compose

## Развертывание
1. Скачиваем файл docker-compose.yml из репозитория https://github.com/Aykes-Dev/foodgram-project-react/blob/master/infra/docker-compose.yml

2. Создает файл .env
```
touch .env
```
3. Записываем в файл переменные окружения
```
POSTGRES_DB=<имя БД>
POSTGRES_USER=<имя пользователя>
POSTGRES_PASSWORD=<пароль>
DB_NAME=<имя БД>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<секретный ключ Django>
DEBUG=<режим DEBUG True/False>
ALLOWED_HOSTS=<разрешенные хосты>
TEST_BASE=<Использование SQLite - True, Postgres - False>
```

4. Запускаем Docker compose
```
sudo docker compose -f docker-compose.yml pull
sudo docker compose -f docker-compose.yml down
sudo docker compose -f docker-compose.yml up -d
```
5. Собираеми уопируем статику, делаем миграции
```
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/static/. /app/backend_static/static/
```
6. Загрузка тегов в БД
```
sudo docker compose -f docker-compose.yml exec backend python manage.py load_tags
```

7. Загрузка ингредиентов в БД:
* из json:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py load_ingredients_json
```
* из csv:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py load_ingredients_scv
```


#### Создано [Андрей Савостьянов](https://github.com/Aykes-Dev)