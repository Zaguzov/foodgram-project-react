# praktikum_new_diplom
http://84.201.142.253/ - развёрнутый проект

http://84.201.142.253/admin/ - админка

Тестовый пользователь:

Логин - zaguzovalex2000@gmail.com

Пароль - zaguzov

Развёртывание:

sh start.sh

Создайте файл .env и заполните. Пример:

POSTGRES_NAME=postgres

POSTGRES_USER=postgres

POSTGRES_PASSWORD=postgres

DB_HOST=postgresql

DB_PORT=5432

Из каталога infra выполните docker-compose up -d

docker-compose exec backend python manage.py makemigrations --noinput users

docker-compose exec backend python manage.py migrate --noinput users

docker-compose exec backend python manage.py makemigrations --noinput recipes

docker-compose exec backend python manage.py migrate --noinput recipes

docker-compose exec backend python manage.py migrate --noinput

docker-compose exec backend python manage.py collectstatic --no-input

Создание суперпользователя - docker-compose exec backend python manage.py createsuperuser

