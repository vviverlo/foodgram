# Foodgram

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
