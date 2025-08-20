## Foodgram — приложение для публикации рецептов

Этот репозиторий содержит полный проект Foodgram: бэкенд на Django/DRF,
одностраничный интерфейс на React и инфраструктуру для запуска в
контейнерах Docker.  Пользователи могут публиковать свои рецепты,
подписываться на авторов, добавлять понравившиеся блюда в избранное и
формировать список покупок.

### Состав проекта

- **backend/** — исходники Django‑приложения.  Здесь определены
  модели (`recipes`, `tags`, `ingredients`, `users` и т. д.),
  сериализаторы, вьюсеты и URL‑маршруты.  Настройки проекта читают
  параметры из переменных окружения, поэтому для запуска в продакшене
  необходимо передать секреты через файл `.env`.
- **frontend/** — исходники SPA на React.  Используется `create‑react‑app`.
  При сборке приложение компилируется в каталог `build/`, а
  контейнер `frontend` публикует эту сборку через простой HTTP‑сервер.
- **nginx/** — конфигурация промежуточного контейнера, который
  проксирует запросы `/api/` и `/admin/` на бэкенд, раздаёт статику и
  передаёт остальные запросы на фронтенд.  Конфигурация находится в
  `nginx/nginx.conf`, а соответствующий Dockerfile — в
  `nginx/Dockerfile`.
- **data/** — примеры исходных данных для загрузки ингредиентов
  (CSV/JSON).  Скрипты миграций предполагают, что ингредиенты будут
  загружены отдельной командой или через административную панель.
- **docs/** — спецификация API и документация Redoc.
- **postman_collection/** — коллекция запросов для Postman.
- **docker‑compose.yml** — описание сервисов для локальной разработки с
  использованием образов, опубликованных на Docker Hub.
- **docker‑compose.production.yml** — описание сервисов для
  продакшен‑деплоя (идентично `docker‑compose.yml` и используется в CI).
- **.github/workflows/foodgram_workflow.yml** — GitHub Actions
  workflow для тестирования, сборки образов и деплоя на удалённый
  сервер.
- **.env.example** — пример файла окружения.  Скопируйте его в `.env`
  и измените значения под свои нужды перед запуском.

### Быстрый старт в Docker

1.  Скопируйте `.env.example` в `.env` и заполните значения
    (`SECRET_KEY`, `POSTGRES_PASSWORD` и другие).
2.  Соберите и запустите сервисы:

    ```bash
    docker compose up -d
    ```

   Будут подняты четыре контейнера: `db` (PostgreSQL), `backend`
   (Django + Gunicorn), `frontend` (React) и `gateway` (nginx).  После
   запуска проект будет доступен по адресу http://127.0.0.1:8000/.

3.  Для применения миграций и загрузки статики выполните:

    ```bash
    docker compose exec backend python manage.py migrate
    docker compose exec backend python manage.py collectstatic --noinput
    docker compose exec backend bash -lc "rm -rf /backend_static/* && cp -r /app/static/. /backend_static/"
    ```

4.  (Опционально) Загрузите ингредиенты из файла:

    ```bash
    docker compose exec backend python manage.py loaddata /app/data/ingredients.json
    ```

### Настройка CI/CD

Для автоматического деплоя проекта на виртуальный сервер используются
GitHub Actions.  Файл `.github/workflows/foodgram_workflow.yml` содержит
следующие этапы:

1. **tests** — проверка стиля кода с помощью flake8 и запуск unit‑тестов
   бэкенда.  Для фронтенда выполняется `npm run test`, если в проекте
   присутствуют тесты.  Используется сервис PostgreSQL.
2. **build_backend**, **build_frontend**, **build_gateway** — сборка и
   публикация Docker‑образов бэкенда, фронтенда и nginx‑шлюза в Docker
   Registry.  Имена образов формируются из вашего логина Docker Hub:
   `${{ secrets.DOCKER_USERNAME }}/foodgram_backend:latest` и т. д.
3. **cleanup** — подключение к серверу по SSH, остановка старых
   контейнеров, очистка ресурсов.
4. **deploy** — копирование файла `docker‑compose.production.yml` на
   сервер и запуск сервисов.  После успешной публикации выполняются
   миграции, сборка и копирование статики.
5. **notify** — отправка уведомления в Telegram о завершении деплоя.

Для работы CI/CD необходимо добавить в настройки репозитория секреты:

- `HOST` — адрес виртуального сервера;
- `USER` — имя пользователя для SSH;
- `SSH_KEY` — приватный SSH‑ключ;
- `SSH_PASSPHRASE` — пароль к ключу (если используется);
- `DOCKER_USERNAME` и `DOCKER_PASSWORD` — логин и пароль Docker Hub;
- `TELEGRAM_TO` и `TELEGRAM_TOKEN` — данные вашего Telegram‑бота для
  уведомлений.

### Полезные команды для разработки

Запуск сервера локально (без Docker):

```bash
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

После запуска API будет доступно на http://127.0.0.1:8000/api/.

### Ссылки

- Исходная спецификация и описание проекта находятся в
  `docs/openapi-schema.yml` и `docs/redoc.html`.
- Коллекция запросов для Postman — в каталоге `postman_collection/`.