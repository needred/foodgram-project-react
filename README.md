# Проект «Продуктовый помощник» - Foodgram
Foodgram - Продуктовый помощник. Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологический стек
![Django-app workflow](https://github.com/needred/foodgram-project-react/actions/workflows/backend.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=008080)](https://jwt.io/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

## Workflow
* build_and_push_to_docker_hub - Сборка и доставка докер-образов на Docker Hub
* deploy - Автоматический деплой проекта на боевой сервер. Выполняется копирование файлов из репозитория на сервер:
* send_message - Отправка уведомления в Telegram

### Подготовка для запуска workflow
Создайте и активируйте виртуальное окружение, обновите pip:
```
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade pip
```
Отредактируйте файл `nginx/default.conf` и в строке `server_name` впишите IP виртуальной машины (сервера).  
Скопируйте подготовленные файлы `docker-compose.yaml` и `nginx/default.conf` из вашего проекта на сервер:
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
sudo mkdir nginx
scp default.conf <username>@<host>/home/<username>/nginx/default.conf
```
В репозитории на Гитхабе добавьте данные в `Settings - Secrets - Actions secrets`:
- ```DOCKER_USERNAME``` - имя пользователя в DockerHub
- ```DOCKER_PASSWORD``` - пароль пользователя в DockerHub
- ```HOST``` - адрес сервера
- ```USER``` - пользователь
- ```SSH_KEY``` - приватный ssh ключ (публичный должен быть на сервере)
- ```PASSPHRASE``` - кодовая фраза для ssh-ключа
- ```DB_ENGINE``` - django.db.backends.postgresql
- ```DB_NAME``` - postgres (по умолчанию)
- ```POSTGRES_USER``` - postgres (по умолчанию)
- ```POSTGRES_PASSWORD``` - postgres (по умолчанию)
- ```DB_HOST``` - db
- ```DB_PORT``` - 5432
- ```SECRET_KEY``` - секретный ключ приложения django (необходимо чтобы были экранированы или отсутствовали скобки)
- ```ALLOWED_HOSTS``` - список разрешенных адресов
- ```TELEGRAM_TO``` - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
- ```TELEGRAM_TOKEN``` - токен бота (получить токен можно у @BotFather, /token, имя бота)
При внесении любых изменений в проект, после коммита и пуша
```
git add .
git commit -m "..."
git push
```
запускается набор блоков команд jobs (см. файл [backend.yml](https://github.com/needred/foodgram-project-react/blob/master/.github/workflows/backend.yml), т.к. команда `git push` является триггером workflow проекта.


## Как развернуть проект на сервере:
Установите соединение с сервером:
```
ssh username@server_address
```
Обновите индекс пакетов APT:
```
sudo apt update
```
и обновите установленные в системе пакеты и установите обновления безопасности:
```
sudo apt upgrade -y 
```
Проверьте статус nginx:
```
sudo service nginx status
```
Если nginx запущен, остановите его:
```
sudo systemctl stop nginx
```
Установите Docker и Docker-compose:
```
sudo apt install docker.io
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```
Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version
```
Создайте папку `nginx`:
```
mkdir nginx
```
### После успешного деплоя:
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone https://github.com/needred/foodgram-project-react.git
cd backend
```
Соберите статические файлы (статику):
```
docker-compose exec backend python manage.py collectstatic --no-input
```
Примените миграции:
```
(опционально) docker-compose exec backend python manage.py makemigrations
```
```
docker-compose exec backend python manage.py migrate --noinput
```
Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
При необходимости наполните базу тестовыми данными из backend/data/:
```
docker-compose exec backend python manage.py load_ingredients
```
и
```
docker-compose exec backend python manage.py load_tags
```

### Тестовые пользователи
Логин: ```admin``` (суперюзер)  
Пароль: ```123456```  

Логин: ```user1```  
Пароль: ```user1123456```  

Логин: ```user2```  
Пароль: ```user2123456```

## Ссылки
### Документация API Foodgram:
http://51.250.28.207/api/docs/redoc.html
### Развёрнутый проект:
http://51.250.28.207  
http://51.250.28.207/admin/

## Об авторе
[needred](https://github.com/needred/)
