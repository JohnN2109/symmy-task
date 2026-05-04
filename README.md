# Symmy Integrator

Async ERP → E-shop synchronization service built with Django, Celery, Redis and PostgreSQL.

---

## Features

- Celery async synchronization
- Product validation
- Delta sync using SHA256 hash
- Retry logic for rate limiting
- Mocked E-shop API
- Docker support

---

## Tech stack

- Django
- Celery
- Redis
- PostgreSQL
- Docker

## Architecture
---
- ERP JSON
↓
- Celery Task
↓
- Validation + Transformation
↓
- Delta Sync
↓
- Mocked E-shop API

---

## Run project

```bash
docker compose up --build
```

---

## Run migrations

```bash
docker compose exec web python manage.py migrate
```

---

## Run synchronization

```bash
docker compose exec web python manage.py shell
```

Then run:

```python
from integrator.tasks import sync_products
sync_products.delay()
```

---

## Run tests

```bash
docker compose exec web python manage.py test
```

---

## Validation rules

- negative price -> invalid
- missing price -> invalid
- duplicate SKU -> invalid
- invalid stock value -> invalid

---

## Notes

The E-shop API is mocked intentionally because the provided API endpoint does not exist.
Synchronization requests are simulated via logging.
