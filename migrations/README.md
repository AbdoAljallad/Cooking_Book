# Migrations

Alembic is initialized for future SQLAlchemy model migrations.

Generated revisions will be stored in `migrations/versions/`.

The migration environment reads the live database URL from `app/config/app_config.toml` through the application settings layer, so migration commands stay aligned with the app configuration.
