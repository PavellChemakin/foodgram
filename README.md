# Foodgram — Продуктовый помощник

**Foodgram** — дипломный проект курса **Backend-разработки** Яндекс.Практикум.  
Это сервис для публикации кулинарных рецептов.  

## Возможности

- публикация и редактирование рецептов;
- подписки на авторов;
- добавление рецептов в избранное;
- формирование списка покупок по выбранным блюдам.

Back-end реализован на **Django REST Framework**, front-end — на **React**.  
Проект разворачивается в **Docker-контейнерах** и готов к установке на удалённый сервер.  
API документирован с помощью **Redoc**.

---

## Структура проекта

- `backend/` — Django-проект: приложения `users`, `recipes`, `api`, миграции, админка.  
- `frontend/` — React-клиент, сборка формирует каталог `build` со статикой.  
- `data/` — предзагруженные ингредиенты в формате CSV. Загружаются командой `manage.py load_ingredients`.  
- `docs/` — документация API в OpenAPI/Redoc.  
- `infra/` — инфраструктура: `docker-compose.yml` (PostgreSQL, backend, frontend, nginx) и `nginx.conf`.  
- `.github/workflows/` — GitHub Actions workflow: сборка образов, публикация на DockerHub, деплой на сервер и уведомления в Telegram.  
- `.env.example` — пример файла окружения.  

---

## Развёртывание локально

1. Установите [Docker](https://www.docker.com/) и [docker-compose](https://docs.docker.com/compose/).  
2. Клонируйте репозиторий и перейдите в каталог `infra`:

   ```bash
   git clone <YOUR_REPOSITORY_URL> foodgram
   cd foodgram/infra
   ```

3. Создайте `.env` в `infra/` на основе `.env.example`:

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

5. Примените миграции, создайте суперюзера и загрузите данные:

   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   docker-compose exec backend python manage.py collectstatic --no-input
   docker-compose exec backend python manage.py load_ingredients
   ```

6. Для работы фронтенда создайте несколько тегов через админ-панель.  

7. Откройте сайт [http://localhost/](http://localhost/).  
   Документация API: [http://localhost/api/docs/](http://localhost/api/docs/).  

---

## Развёртывание на сервере

Автодеплой выполняется через GitHub Actions (`.github/workflows/main.yml`).  
Необходимые секреты репозитория:

- **DOCKER_USERNAME**, **DOCKER_PASSWORD** — доступ к DockerHub.  
- **HOST**, **USER** — IP и пользователь сервера.  
- **SSH_KEY**, **SSH_PASSPHRASE** — приватный ключ SSH.  
- **TELEGRAM_TO**, **TELEGRAM_TOKEN** — параметры Telegram-бота.  
- **SECRET_KEY**, **DB_ENGINE**, **DB_NAME**, **POSTGRES_USER**, **POSTGRES_PASSWORD**, **DB_HOST**, **DB_PORT** — переменные окружения.  

При пуше в `main` workflow:  
1. собирает образ backend и пушит в DockerHub;  
2. подключается по SSH к серверу, обновляет образы и контейнеры, пересоздаёт `.env`;  
3. уведомляет в Telegram.  

`infra/nginx.conf` настроен для домена `foodgramvm.serveirc.com` и IP `84.252.141.185`. При необходимости измените.  

---

## Безопасность

- Файл `.env` не хранится в репозитории.  
- В `settings.py` для продакшена укажите `DEBUG=False` и заполните `ALLOWED_HOSTS`.  
- Настройте DNS-запись домена на IP сервера.  

---

## Авторы

Проект основан на шаблоне **Foodgram** (Яндекс.Практикум).  
Версия адаптирована для продакшн-развёртывания на домене `foodgramvm.serveirc.com`.  
