# Symmy Integrator

## Run project

```bash
docker compose up --build
```

## Run migrations

```bash
docker compose exec web python manage.py migrate
```

## Run sync

```bash
docker compose exec web python manage.py shell
```

```python
from integrator.tasks import sync_products
sync_products.delay()
```

---

## Features

- Celery async synchronization
- Delta sync using SHA256 hash
- Mocked e-shop API
- Retry logic for 429 rate limiting
- Product transformation:
  - stock aggregation
  - 21% VAT
  - default color fallback