Generic single-database configuration.

1. Make the first migration with the following command:

```bash
alembic revision --autogenerate -m "initial migration"

```

2. Make other migrations with the following command:
```bash
alembic revision --autogenerate -m "my new migration"

```

3. Upgrade the database with the following command:

```bash
alembic upgrade head

```