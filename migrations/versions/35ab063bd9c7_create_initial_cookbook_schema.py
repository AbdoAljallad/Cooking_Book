"""create initial cookbook schema

Revision ID: 35ab063bd9c7
Revises: 
Create Date: 2026-03-29 19:31:23.965041
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '35ab063bd9c7'
down_revision = None
branch_labels = None
depends_on = None

CURRENT_TIMESTAMP = sa.text("CURRENT_TIMESTAMP")
MYSQL_TABLE_KW = {
    "mysql_engine": "InnoDB",
    "mysql_charset": "utf8mb4",
}


def upgrade() -> None:
    op.create_table('categories',
    sa.Column('slug', sa.String(length=191), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    sa.UniqueConstraint('slug', name=op.f('uq_categories_slug')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_categories_is_active', 'categories', ['is_active'], unique=False)
    op.create_index('ix_categories_sort_order', 'categories', ['sort_order'], unique=False)
    op.create_table('languages',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('native_name', sa.String(length=100), nullable=False),
    sa.Column('is_rtl', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_languages')),
    sa.UniqueConstraint('code', name=op.f('uq_languages_code')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_languages_is_active', 'languages', ['is_active'], unique=False)
    op.create_table('profiles',
    sa.Column('display_name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=191), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_profiles')),
    sa.UniqueConstraint('email', name=op.f('uq_profiles_email')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_profiles_is_active', 'profiles', ['is_active'], unique=False)
    op.create_table('tags',
    sa.Column('slug', sa.String(length=191), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
    sa.UniqueConstraint('slug', name=op.f('uq_tags_slug')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_tags_is_active', 'tags', ['is_active'], unique=False)
    op.create_table('units',
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('symbol', sa.String(length=50), nullable=True),
    sa.Column('is_fractional', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_units')),
    sa.UniqueConstraint('code', name=op.f('uq_units_code')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_units_is_active', 'units', ['is_active'], unique=False)
    op.create_table('app_settings',
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('ui_language_id', sa.Integer(), nullable=False),
    sa.Column('theme_name', sa.String(length=50), nullable=False),
    sa.Column('layout_direction', sa.String(length=10), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], name=op.f('fk_app_settings_profile_id_profiles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ui_language_id'], ['languages.id'], name=op.f('fk_app_settings_ui_language_id_languages'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_app_settings')),
    sa.UniqueConstraint('profile_id', name=op.f('uq_app_settings_profile_id')),
    **MYSQL_TABLE_KW,
    )
    op.create_index(op.f('ix_app_settings_ui_language_id'), 'app_settings', ['ui_language_id'], unique=False)
    op.create_table('category_translations',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=191), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_category_translations_category_id_categories'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name=op.f('fk_category_translations_language_id_languages'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_category_translations')),
    sa.UniqueConstraint('category_id', 'language_id', name='uq_category_language'),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_category_translations_name', 'category_translations', ['name'], unique=False)
    op.create_table('ingredients',
    sa.Column('slug', sa.String(length=191), nullable=False),
    sa.Column('default_unit_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['default_unit_id'], ['units.id'], name=op.f('fk_ingredients_default_unit_id_units'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ingredients')),
    sa.UniqueConstraint('slug', name=op.f('uq_ingredients_slug')),
    **MYSQL_TABLE_KW,
    )
    op.create_index(op.f('ix_ingredients_default_unit_id'), 'ingredients', ['default_unit_id'], unique=False)
    op.create_index('ix_ingredients_is_active', 'ingredients', ['is_active'], unique=False)
    op.create_table('recipes',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('image_path', sa.String(length=500), nullable=True),
    sa.Column('prep_time_minutes', sa.Integer(), nullable=False),
    sa.Column('cook_time_minutes', sa.Integer(), nullable=False),
    sa.Column('base_servings', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('difficulty_level', sa.Enum('easy', 'medium', 'hard', name='difficulty_level_enum', native_enum=False, create_constraint=True), nullable=False),
    sa.Column('source_type', sa.Enum('original', 'imported', 'adapted', name='recipe_source_type_enum', native_enum=False, create_constraint=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by_profile_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.CheckConstraint('base_servings > 0', name=op.f('ck_recipes_base_servings_positive')),
    sa.CheckConstraint('cook_time_minutes >= 0', name=op.f('ck_recipes_cook_time_nonnegative')),
    sa.CheckConstraint('prep_time_minutes >= 0', name=op.f('ck_recipes_prep_time_nonnegative')),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_recipes_category_id_categories'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['created_by_profile_id'], ['profiles.id'], name=op.f('fk_recipes_created_by_profile_id_profiles'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipes')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_recipes_category_active', 'recipes', ['category_id', 'is_active'], unique=False)
    op.create_index('ix_recipes_created_by_profile_id', 'recipes', ['created_by_profile_id'], unique=False)
    op.create_index(op.f('ix_recipes_is_active'), 'recipes', ['is_active'], unique=False)
    op.create_table('tag_translations',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name=op.f('fk_tag_translations_language_id_languages'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name=op.f('fk_tag_translations_tag_id_tags'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tag_translations')),
    sa.UniqueConstraint('tag_id', 'language_id', name='uq_tag_language'),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_tag_translations_name', 'tag_translations', ['name'], unique=False)
    op.create_table('unit_translations',
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('abbreviation', sa.String(length=50), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name=op.f('fk_unit_translations_language_id_languages'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['unit_id'], ['units.id'], name=op.f('fk_unit_translations_unit_id_units'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_unit_translations')),
    sa.UniqueConstraint('unit_id', 'language_id', name='uq_unit_language'),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_unit_translations_name', 'unit_translations', ['name'], unique=False)
    op.create_table('favorites',
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], name=op.f('fk_favorites_profile_id_profiles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_favorites_recipe_id_recipes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('profile_id', 'recipe_id', name=op.f('pk_favorites')),
    **MYSQL_TABLE_KW,
    )
    op.create_table('ingredient_translations',
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=191), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], name=op.f('fk_ingredient_translations_ingredient_id_ingredients'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name=op.f('fk_ingredient_translations_language_id_languages'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ingredient_translations')),
    sa.UniqueConstraint('ingredient_id', 'language_id', name='uq_ingredient_language'),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_ingredient_translations_name', 'ingredient_translations', ['name'], unique=False)
    op.create_table('recipe_ingredients',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=True),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('is_scalable', sa.Boolean(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('preparation_note', sa.String(length=255), nullable=True),
    sa.Column('text_override', sa.String(length=120), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.CheckConstraint('quantity IS NULL OR quantity >= 0', name=op.f('ck_recipe_ingredients_quantity_nonnegative')),
    sa.CheckConstraint('sort_order >= 0', name=op.f('ck_recipe_ingredients_sort_order_nonnegative')),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], name=op.f('fk_recipe_ingredients_ingredient_id_ingredients'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_ingredients_recipe_id_recipes'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['unit_id'], ['units.id'], name=op.f('fk_recipe_ingredients_unit_id_units'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipe_ingredients')),
    **MYSQL_TABLE_KW,
    )
    op.create_index(op.f('ix_recipe_ingredients_ingredient_id'), 'recipe_ingredients', ['ingredient_id'], unique=False)
    op.create_index('ix_recipe_ingredients_recipe_sort_order', 'recipe_ingredients', ['recipe_id', 'sort_order'], unique=False)
    op.create_index(op.f('ix_recipe_ingredients_unit_id'), 'recipe_ingredients', ['unit_id'], unique=False)
    op.create_table('recipe_notes',
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('note_text', sa.Text(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], name=op.f('fk_recipe_notes_profile_id_profiles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_notes_recipe_id_recipes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipe_notes')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_recipe_notes_profile_recipe', 'recipe_notes', ['profile_id', 'recipe_id'], unique=True)
    op.create_table('recipe_ratings',
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.CheckConstraint('rating >= 1 AND rating <= 5', name=op.f('ck_recipe_ratings_rating_range')),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], name=op.f('fk_recipe_ratings_profile_id_profiles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_ratings_recipe_id_recipes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipe_ratings')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_recipe_ratings_profile_recipe', 'recipe_ratings', ['profile_id', 'recipe_id'], unique=True)
    op.create_table('recipe_steps',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('estimated_minutes', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.CheckConstraint('estimated_minutes IS NULL OR estimated_minutes >= 0', name=op.f('ck_recipe_steps_estimated_minutes_nonnegative')),
    sa.CheckConstraint('sort_order >= 0', name=op.f('ck_recipe_steps_sort_order_nonnegative')),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_steps_recipe_id_recipes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipe_steps')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_recipe_steps_recipe_sort_order', 'recipe_steps', ['recipe_id', 'sort_order'], unique=True)
    op.create_table('recipe_tags',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_tags_recipe_id_recipes'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name=op.f('fk_recipe_tags_tag_id_tags'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('recipe_id', 'tag_id', name=op.f('pk_recipe_tags')),
    **MYSQL_TABLE_KW,
    )
    op.create_table('recipe_translations',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('short_description', sa.String(length=500), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.CheckConstraint('length(title) > 0', name=op.f('ck_recipe_translations_title_nonempty')),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name=op.f('fk_recipe_translations_language_id_languages'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_translations_recipe_id_recipes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipe_translations')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_recipe_translations_recipe_language', 'recipe_translations', ['recipe_id', 'language_id'], unique=True)
    op.create_index('ix_recipe_translations_title', 'recipe_translations', ['title'], unique=False)
    op.create_table('recipe_step_translations',
    sa.Column('recipe_step_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('instruction', sa.Text(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=CURRENT_TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name=op.f('fk_recipe_step_translations_language_id_languages'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['recipe_step_id'], ['recipe_steps.id'], name=op.f('fk_recipe_step_translations_recipe_step_id_recipe_steps'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipe_step_translations')),
    **MYSQL_TABLE_KW,
    )
    op.create_index('ix_recipe_step_translations_recipe_step_language', 'recipe_step_translations', ['recipe_step_id', 'language_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_recipe_step_translations_recipe_step_language', table_name='recipe_step_translations')
    op.drop_table('recipe_step_translations')
    op.drop_index('ix_recipe_translations_title', table_name='recipe_translations')
    op.drop_index('ix_recipe_translations_recipe_language', table_name='recipe_translations')
    op.drop_table('recipe_translations')
    op.drop_table('recipe_tags')
    op.drop_index('ix_recipe_steps_recipe_sort_order', table_name='recipe_steps')
    op.drop_table('recipe_steps')
    op.drop_index('ix_recipe_ratings_profile_recipe', table_name='recipe_ratings')
    op.drop_table('recipe_ratings')
    op.drop_index('ix_recipe_notes_profile_recipe', table_name='recipe_notes')
    op.drop_table('recipe_notes')
    op.drop_index(op.f('ix_recipe_ingredients_unit_id'), table_name='recipe_ingredients')
    op.drop_index('ix_recipe_ingredients_recipe_sort_order', table_name='recipe_ingredients')
    op.drop_index(op.f('ix_recipe_ingredients_ingredient_id'), table_name='recipe_ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_index('ix_ingredient_translations_name', table_name='ingredient_translations')
    op.drop_table('ingredient_translations')
    op.drop_table('favorites')
    op.drop_index('ix_unit_translations_name', table_name='unit_translations')
    op.drop_table('unit_translations')
    op.drop_index('ix_tag_translations_name', table_name='tag_translations')
    op.drop_table('tag_translations')
    op.drop_index(op.f('ix_recipes_is_active'), table_name='recipes')
    op.drop_index('ix_recipes_created_by_profile_id', table_name='recipes')
    op.drop_index('ix_recipes_category_active', table_name='recipes')
    op.drop_table('recipes')
    op.drop_index('ix_ingredients_is_active', table_name='ingredients')
    op.drop_index(op.f('ix_ingredients_default_unit_id'), table_name='ingredients')
    op.drop_table('ingredients')
    op.drop_index('ix_category_translations_name', table_name='category_translations')
    op.drop_table('category_translations')
    op.drop_index(op.f('ix_app_settings_ui_language_id'), table_name='app_settings')
    op.drop_table('app_settings')
    op.drop_index('ix_units_is_active', table_name='units')
    op.drop_table('units')
    op.drop_index('ix_tags_is_active', table_name='tags')
    op.drop_table('tags')
    op.drop_index('ix_profiles_is_active', table_name='profiles')
    op.drop_table('profiles')
    op.drop_index('ix_languages_is_active', table_name='languages')
    op.drop_table('languages')
    op.drop_index('ix_categories_sort_order', table_name='categories')
    op.drop_index('ix_categories_is_active', table_name='categories')
    op.drop_table('categories')
