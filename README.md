# Foodgram – продуктовый помощник

**Foodgram** – это учебный проект из курса разработчика на Django, представляющий собой сервис для публикации кулинарных рецептов. Пользователи могут создавать и редактировать свои рецепты, подписываться на любимых авторов, добавлять понравившиеся блюда в избранное и формировать список покупок по выбранным рецептам. Проект состоит из back‑end части на Django REST Framework и front‑end приложения на React, упакованных в Docker‑контейнеры и готовых к развёртыванию на удалённом сервере.

## Структура проекта

* `backend/` – исходный код back‑end сервиса. Включает Django‑проект, приложения `users`, `recipes` и `api`, файлы миграций, админку и скрипт `manage.py`. Докерфайл описывает сборку образа с Gunicorn.
* `frontend/` – исходный код React‑клиента. При сборке генерирует каталог `build` с оптимизированными статическими файлами.
* `data/` – предзагруженные ингредиенты в формате CSV. Их можно загрузить в базу командой `manage.py load_ingredients`.
* `docs/` – документация API в формате OpenAPI/Redoc.
* `infra/` – конфигурация инфраструктуры. Содержит `docker-compose.yml` для развёртывания четырёх контейнеров (PostgreSQL, back‑end, front‑end и nginx) и `nginx.conf` для проксирования запросов и раздачи статики.
* `.github/workflows/` – GitHub Actions workflow для сборки образа, публикации его на Docker Hub, деплоя на удалённый сервер и отправки уведомления в Telegram.
* `.env.example` – пример файла конфигурации окружения для контейнеров.

## Как развернуть Foodgram локально

1. Установите [Docker](https://www.docker.com/) и [docker‑compose](https://docs.docker.com/compose/).
2. Склонируйте репозиторий и перейдите в каталог `infra`:

   ```bash
   git clone <YOUR_REPOSITORY_URL> foodgram
   cd foodgram/infra
   ```

3. Создайте файл `.env` в каталоге `infra` на основе `.env.example` и заполните его значениями (секретный ключ Django, параметры базы данных и т. д.). Например:

   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=foodgram
   POSTGRES_USER=foodgram
   POSTGRES_PASSWORD=foodgram
   DB_HOST=db
   DB_PORT=5432
   ```

4. Запустите контейнеры:

   ```bash
   docker-compose up -d --build
   ```

5. Примените миграции, создайте суперпользователя и загрузите ингредиенты:

   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   docker-compose exec backend python manage.py collectstatic --no-input
   docker-compose exec backend python manage.py load_ingredients
   ```

6. Откройте сайт в браузере по адресу [http://localhost/](http://localhost/) (или по адресу, указанному в `nginx.conf`). Документация API доступна по адресу `http://localhost/api/docs/`.

## Развёртывание на сервере

В репозитории находится GitHub Actions workflow `.github/workflows/main.yml`, который автоматизирует сборку и деплой приложения на ваш сервер. Для его работы необходимо создать секреты в настройках репозитория:

* **DOCKER_USERNAME**, **DOCKER_PASSWORD** – учётные данные Docker Hub.
* **HOST** – публичный IP‑адрес вашего сервера.
* **USER** – имя пользователя на сервере (например, `yc-user`).
* **SSH_KEY** – приватный ключ для SSH‑доступа к серверу.
* **SSH_PASSPHRASE** – пароль к приватному ключу (если установлен).
* **TELEGRAM_TO**, **TELEGRAM_TOKEN** – данные для отправки уведомлений о деплое в Telegram.
* **SECRET_KEY**, **DB_ENGINE**, **DB_NAME**, **POSTGRES_USER**, **POSTGRES_PASSWORD**, **DB_HOST**, **DB_PORT** – переменные окружения для приложения.

После пуша в ветку `main` GitHub Actions выполнит следующие шаги:

1. Соберёт образ back‑end приложения и отправит его в Docker Hub под тегом `${{ secrets.DOCKER_USERNAME }}/foodgram_backend:latest`.
2. Подключится по SSH к серверу, обновит образ, перезапустит контейнеры и заново пересоздаст файл `.env` с заданными параметрами.
3. Отправит уведомление в Telegram о успешном деплое.

Сервер должен быть настроен на получение входящих запросов по 80‑му порту. Файл `infra/nginx.conf` уже содержит конфигурацию для домена `foodgramvm.serveirc.com` и IP‑адреса `84.252.141.185`. При необходимости замените эти значения на свои.

## Замечания по безопасности

* **Не добавляйте приватные ключи и пароли в репозиторий.** Файл `.env` должен быть исключён из контроля версий и храниться только на сервере.
* Настройте DNS‑запись для вашего домена, чтобы он указывал на IP‑адрес сервера.
* В `settings.py` установите `DEBUG=False` в продакшне и заполните список `ALLOWED_HOSTS` актуальными доменами.

## Авторы

Этот репозиторий основан на учебном шаблоне *Foodgram* (Яндекс.Практикум). Финальная версия адаптирована для развёртывания на домене `foodgramvm.serveirc.com` с учётом пользовательских настроек.