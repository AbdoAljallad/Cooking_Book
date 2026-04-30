# Premium Cookbook Desktop App

Premium multilingual desktop cookbook application built with Python, PySide6, MySQL, SQLAlchemy, and Alembic.

## Features of this starter

- Scalable `app/` package structure
- Dedicated theme system from day one
- Reusable UI component placeholders
- Structured and validated MySQL configuration layer
- Database, repositories, services, models, and tests separated cleanly
- Modern data-bound desktop screens for browsing, creating, and viewing recipes
- SQLAlchemy engine, session, and health-check helpers
- Alembic bootstrap files for future migrations

## Project structure

```text
Cooking_Book/
├── app/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── ui/
│   │   ├── components/
│   │   ├── themes/
│   │   └── windows/
│   └── utils/
├── assets/
│   ├── fonts/
│   ├── icons/
│   └── images/
├── migrations/
├── tests/
├── main.py
└── requirements.txt
```

## Install

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Use Python 3.11+ so the built-in `tomllib` module is available.

For MySQL servers using the default modern authentication plugins such as `caching_sha2_password`, `cryptography` is also required and is included in `requirements.txt`.

## Configure MySQL

Update `app/config/app_config.toml` or copy from `app/config/app_config.toml.example`:

```toml
[database]
driver = "mysql+pymysql"
host = "127.0.0.1"
port = 3306
name = "cookbook_db"
user = "root"
password = "your_password"
charset = "utf8mb4"
connect_timeout = 3
pool_pre_ping = true
pool_recycle = 1800
pool_size = 5
max_overflow = 10
echo = false
```

The application validates these values when loading settings. Startup does not crash if the database is offline or misconfigured for connectivity; the UI shows a clean status message instead.

## Run the starter app

```bash
python main.py
```

## Validate the database connection

```bash
python -c "from app.database.health import check_database_connection; result = check_database_connection(); print(result.ok, result.message); print(result.error or '')"
```

This performs a safe `SELECT 1` probe and returns a clear success or failure result without crashing the app.

## Alembic

Alembic is initialized with:

- `alembic.ini`
- `migrations/env.py`
- `migrations/script.py.mako`
- `migrations/versions/`

The migration environment reads the database URL from the same app config used by the application.

With the ORM models now defined, the initial migration baseline is:

- `35ab063bd9c7_create_initial_cookbook_schema.py`

To apply the initial schema to MySQL:

```bash
python -m alembic upgrade head
```

To roll it back completely:

```bash
python -m alembic downgrade base
```

To generate future revisions after model changes:

```bash
python -m alembic revision --autogenerate -m "describe schema change"
```

If your local MySQL server is offline and you only want to validate migration mechanics against a disposable database, you can override the Alembic target URL temporarily:

```bash
$env:ALEMBIC_DATABASE_URL='sqlite:///migration_validation.db'
python -m alembic upgrade head
python -m alembic downgrade base
```

To verify the MySQL schema after applying the baseline, inspect the resulting tables in MySQL and confirm they match the ORM metadata:

```bash
python -c "import app.models; from app.database.base import Base; print(sorted(Base.metadata.tables.keys()))"
```

## Seed reference data

After the schema is migrated, run the reference-data seed:

```bash
python -m app.seeds
```

The seed is idempotent. Running it multiple times updates the same bootstrap records instead of creating duplicates.

It inserts:

- Languages: `en`, `ar`, `ru`
- One default local profile: `local@cookbook.app`
- One default app setting row linked to that profile
- Main recipe categories with English, Arabic, and Russian translations
- Common measurement units with English, Arabic, and Russian translations
- Starter tags with English, Arabic, and Russian translations

To verify seeded data:

```bash
python -c "import app.models; from app.database.session import create_session; from app.models import Language, Profile, Category, Unit, Tag, Recipe; s=create_session(); print('languages', s.query(Language).count()); print('profiles', s.query(Profile).count()); print('categories', s.query(Category).count()); print('units', s.query(Unit).count()); print('tags', s.query(Tag).count()); print('recipes', s.query(Recipe).count()); s.close()"
```

## Repositories

The read-oriented repository layer lives in `app/repositories/` and stays independent from PySide UI code.

- `LanguageRepository`, `ProfileRepository`, and `AppSettingRepository` return ORM entities for simple lookups.
- `CategoryRepository`, `UnitRepository`, and `TagRepository` return localized projection objects so translated names are explicit.
- `RecipeRepository` exposes lightweight list/search projections for future UI screens and a full `get_by_id()` method for detailed loading.

Run repository tests with:

```bash
python -m pytest -q
```

## Home screen

The initial data-bound Home screen now reads through the service layer rather than directly through repositories.

- `AppContextService` resolves the default profile, active UI language, and theme-related context.
- `CategoryService`, `TagService`, and `RecipeService` provide focused read operations for the UI.
- `HomeService` assembles the dashboard payload used by the Home screen.
- Clicking a recipe card opens the dedicated Recipe Details screen.

Run the application visually with:

```bash
python main.py
```

If there are no recipes yet, the Home screen still renders seeded categories and tags plus a polished empty state instead of a blank page.

The Recipe Details screen shows translated recipe content, category, tags, ingredients, ordered steps, and recipe metadata. If an image is missing, a styled placeholder is shown instead of an empty frame.

The Recipe Details screen also supports display-time servings scaling. Adjusting the target servings updates ingredient quantities instantly without mutating stored recipe data.

The Home screen now supports real recipe search and category filtering through the service and repository layers. Search matches recipe title and short description for the active UI language, category chips toggle the active category filter, and clearing filters restores the full list.

The catalog grid wraps recipe cards based on available window width and avoids horizontal scrolling. Recipe cards use consistent image frames, equal placeholder sizing, and compact tag display.

Recipe Details now also supports personal interactions for the default local profile: favorite toggling, a 1-to-5 rating, and a lightweight personal note. A dedicated Favorites view is available from the main shell and reuses the existing recipe cards.

The app also includes a dedicated Settings screen for the default local profile. Theme and language preferences persist to `app_settings`, theme changes apply immediately to the running application, and language selection already updates data language and layout direction while preparing the codebase for fuller UI localization later.

The settings flow now explicitly supports:

- English
- Arabic
- Russian

The selected language is stored in the database-backed profile settings and restored on the next launch. In this step, the shared shell labels, settings workflow, search controls, and the new recipe-image workflow are localized. The rest of the UI is prepared for the next broader localization pass through the centralized helpers in `app/utils/i18n.py`.

The main application shell now uses a persistent side navigation panel for Catalog, Add Recipe, Favorites, Categories, and Settings. The Categories page is intentionally a polished placeholder until category management is implemented.

The database status badge is monitored automatically while the app is running. A lightweight background check updates the badge when MySQL becomes available or unavailable, and the current page reloads automatically after reconnection.

On successful database connection, the app performs a safe startup maintenance check. Missing tables are created with SQLAlchemy metadata, and missing reference rows are inserted through the idempotent seed layer. The check does not truncate tables, delete recipes, or reset user-created content.

Translated database content uses English as the default fallback. If Arabic or Russian text is missing for recipes, categories, tags, units, ingredients, or steps, the service/repository layer resolves the English value before the UI renders it.

## Create recipe flow

The app now includes a dedicated Add Recipe screen reached from the top-bar `Add Recipe` button.

- The UI collects English, Arabic, and Russian recipe content.
- Recipe creation now stores English, Arabic, and Russian recipe translations through the existing translation tables.
- English, Arabic, and Russian titles are required for new recipes.
- Recipe steps support English, Arabic, and Russian instructions.
- Ingredient matching and creation support Russian ingredient names in addition to English and Arabic.
- Categories, tags, and units are loaded through services and repositories.
- Ingredients are entered inline. Existing ingredients are reused automatically when the entered English or Arabic name matches an existing translation.
- If an ingredient does not exist yet, the create flow inserts a new `Ingredient` plus the provided translations.
- Steps are created in order with required English instructions and optional Arabic instructions.
- On success, the new recipe is saved with translations, tag links, ingredients, and steps, then the app opens the Recipe Details screen for the new record.

Validation rules currently include:

- English recipe title is required
- Arabic recipe title is required
- Russian recipe title is required
- category is required
- prep and cook times must be zero or greater
- base servings must be greater than zero
- at least one ingredient is required
- at least one step is required
- each step requires English, Arabic, and Russian instructions
- each ingredient needs an English name
- ingredient quantities must be zero or greater
- each step needs an English instruction
- step estimated minutes must be zero or greater

To test the full create flow visually:

```bash
python main.py
```

Then:

1. Click `Add Recipe`
2. Fill the form and save
3. Confirm the app opens the new Recipe Details screen
4. Return Home and confirm the recipe appears in the list

## Managed recipe images

Recipe images are now handled through an application-managed workflow instead of depending on external file paths.

- On the Add Recipe screen, the user can provide an image by:
  - choosing a file from the file picker
  - pasting an image from the clipboard
  - dragging and dropping an image file into the image panel
- The selected image is previewed before save.
- After the recipe is created and receives a database ID, the image is copied into:
  - `assets/images/recipes/<recipe_id>.png`
- The database stores this managed relative path, not the original external source path.
- If a recipe has no image, the app uses a generated placeholder image stored under:
  - `assets/images/placeholders/no_image.png`

The placeholder uses a single solid background and centered English text:

- `No Image`

This placeholder is used consistently on:

- Home recipe cards
- Favorites recipe cards
- Recipe Details

To test the image workflow visually:

1. Open `Add Recipe`
2. In the image section, try one of:
   - `Choose Image`
   - `Paste from Clipboard`
   - drag and drop an image onto the image card
3. Save the recipe
4. Confirm that:
   - the recipe opens successfully
   - the image is shown on the details screen
   - the stored file exists in `assets/images/recipes/`
   - the file name matches the recipe ID
5. Create a recipe without an image and confirm the `No Image` placeholder appears on Home, Favorites, and Details

## Servings scaling

Servings scaling is handled in the service layer and applied only for display on the Recipe Details screen.

- Base servings remain the persisted recipe value.
- The selected servings value is controlled in the UI.
- Scalable numeric ingredients follow: `new_quantity = base_quantity * (target_servings / base_servings)`.
- Ingredients with `quantity_text_override` such as `To taste` are shown as-is.
- Ingredients marked `is_scalable = false` keep their original quantity.
- The database is never updated when the user changes servings in the details view.

To test it visually:

1. Open a recipe details screen
2. Use the servings control in the Recipe Snapshot section
3. Confirm ingredient quantities update immediately
4. Confirm text-only and non-scalable ingredients stay unchanged

## Theme architecture

- Theme definitions live in `app/ui/themes/builtins.py`
- Shared design tokens are modeled in `app/ui/themes/base.py`
- Stylesheet generation is centralized in `app/ui/themes/styles.py`
- Runtime theme selection and application are handled by `app/ui/themes/manager.py`

This keeps colors, spacing, radius, and typography out of individual screens so light, dark, and future custom themes can be added without rewriting window code.

## Next steps

- Add servings scaling behavior on the details screen
- Add favorites, notes, and ratings workflows
- Add i18n translation files and RTL-aware screen flows
