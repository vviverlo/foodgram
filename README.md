# Foodcom

**Food Assistant** — a web application for publishing and sharing recipes. Users can create recipe cards with ingredients and tags, follow authors, add recipes to favorites, and build a shopping list from selected dishes.

**Live demo:** https://foodikson.mooo.com

## Tech stack

**Backend:** Python 3.12, Django 4.2, Django REST Framework, Djoser (authentication), django-filter, Gunicorn, PostgreSQL (production), Pillow.

**Frontend:** React 17, React Router.

**Infrastructure:** Docker, Docker Compose, Nginx, CI/CD (GitHub Actions).

## Key takeaways

- Designed and implemented a REST API with authentication, filtering, and role-based access
- Built a full-stack app with Docker-based deployment and automated CI/CD via GitHub Actions
- Deployed the project to a production server with Nginx, PostgreSQL, and HTTPS

## Local UI and API docs

From the `infra` directory:

```bash
docker compose up
```

The `frontend` container builds static assets into `frontend/build` and exits. The `nginx` container serves the site on port 80.

- **Frontend:** http://localhost
- **ReDoc (API specification):** http://localhost/api/docs/

## Production deployment

General flow: clone the repository on a VPS, configure `.env`, build the frontend, and start containers from `docker-compose.production.yml`. The backend image can be built on the server or pulled from Docker Hub (as in CI).

1. **Clone and environment variables**

```bash
git clone https://github.com/vviverlo/foodgram.git foodcom && cd foodcom
cp infra/.env.example infra/.env
```

Edit `infra/.env`: database credentials, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DEBUG=False`, optionally `BACKEND_IMAGE` (Docker Hub image), `DJANGO_CSRF_TRUSTED_ORIGINS` for HTTPS.

2. **Build the frontend**

```bash
cd frontend && npm ci && npm run build && cd ..
```

3. **SSL (Let's Encrypt)**

Certificates in `nginx.production.conf` are expected at `/etc/letsencrypt/live/foodikson.mooo.com`. Obtain certificates with certbot and adjust `server_name` and paths in the config if needed.

4. **Start the stack**

```bash
cd infra
docker compose -f docker-compose.production.yml --env-file .env up -d
```

On first run, apply migrations and collect static files for the backend (`docker compose exec backend …`) if not handled by the image or entrypoint.

5. **Updates (same as CI)**

On the server: `git pull`, then from `infra`:

```bash
docker compose -f docker-compose.production.yml --env-file .env pull
docker compose -f docker-compose.production.yml --env-file .env up -d
```

## Run backend locally (without Docker)

Requires Python 3.12.

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If PostgreSQL environment variables are not set, SQLite is used (`db.sqlite3` in the `backend` directory).

```bash
export DJANGO_SECRET_KEY="local-secret-key"
python manage.py migrate
python manage.py load_ingredients
python manage.py load_tags
python manage.py runserver
```

For PostgreSQL, set `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT` (see `infra/.env.example`).

## Author

- **Name:** Islam Ramazanov
- **Telegram:** [@arkis03](https://t.me/arkis03)
- **GitHub:** [vviverlo](https://github.com/vviverlo)
