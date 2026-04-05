# Foodgram

«Продуктовый помощник»: веб-приложение для публикации рецептов. Пользователи могут создавать карточки рецептов с ингредиентами и тегами, подписываться на авторов, добавлять рецепты в избранное и формировать список покупок по выбранным блюдам.

## Стек технологий

**Бэкенд:** Python 3.12, Django 4.2, Django REST Framework, Djoser (аутентификация), django-filter, Gunicorn, PostgreSQL (продакшен), Pillow.

**Фронтенд:** React 17, React Router.

**Инфраструктура:** Docker, Docker Compose, Nginx, CI/CD (GitHub Actions).

## Локальный просмотр UI и документации API

Из каталога `infra` выполните:

```bash
docker compose up
```

Контейнер `frontend` соберёт статику фронтенда в `frontend/build` и завершится. Контейнер `nginx` отдаёт сайт на порту 80.

- **Фронтенд:** http://localhost  
- **ReDoc (спецификация API):** http://localhost/api/docs/

## Развёртывание на сервере

Общая схема: на VPS клонируется репозиторий, настраивается `.env`, собирается фронтенд, поднимаются контейнеры из `docker-compose.production.yml`. Образ бэкенда можно собирать на сервере или тянуть с Docker Hub (как в CI).

1. **Клонирование и переменные окружения**

   ```bash
   git clone https://github.com/vviverlo/foodgram.git foodgram && cd foodgram
   cp infra/.env.example infra/.env
   ```

   Отредактируйте `infra/.env`: пароли БД, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DEBUG=False`, при необходимости `BACKEND_IMAGE` (образ с Docker Hub), `DJANGO_CSRF_TRUSTED_ORIGINS` для HTTPS.

2. **Сборка фронтенда**

   ```bash
   cd frontend && npm ci && npm run build && cd ..
   ```

3. **SSL (Let’s Encrypt)**  
   Сертификаты в `nginx.production.conf` ожидаются в `/etc/letsencrypt/live/foodikson.mooo.com`. Получите сертификаты (certbot) и при необходимости поправьте `server_name` и пути в конфиге.

4. **Запуск**

   ```bash
   cd infra
   docker compose -f docker-compose.production.yml --env-file .env up -d
   ```

   При первом запуске выполните миграции и соберите статику бэкенда (через `docker compose exec backend …`), если это не сделано в образе/entrypoint.

5. **Обновление (как в CI)**  
   На сервере: `git pull`, затем в `infra`:

   ```bash
   docker compose -f docker-compose.production.yml --env-file .env pull
   docker compose -f docker-compose.production.yml --env-file .env up -d
   ```

## Запуск бэкенда локально (без Docker)

Требуется Python 3.12.

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Без переменных PostgreSQL в окружении используется SQLite (`db.sqlite3` в каталоге `backend`).

```bash
export DJANGO_SECRET_KEY="локальный-секрет"
python manage.py migrate
python manage.py load_ingredients
python manage.py load_tags
python manage.py runserver
```

Для работы с PostgreSQL задайте `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT` (см. `infra/.env.example`).

## Ссылка на развёрнутый проект

- **https://foodikson.mooo.com**

## Автор

- **Имя:** Ислам
- **Контакты:** Telegram:@aarkis03 / email / GitHub
