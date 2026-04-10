from __future__ import annotations

from sqlalchemy import select

from app.models import Ingredient, IngredientTranslation, Language
from app.repositories.base import BaseRepository


class IngredientRepository(BaseRepository[Ingredient]):
    def get_by_translation_name(
        self,
        name: str,
        language_code: str,
    ) -> Ingredient | None:
        normalized = name.strip()
        if not normalized:
            return None

        statement = (
            select(Ingredient)
            .join(IngredientTranslation, IngredientTranslation.ingredient_id == Ingredient.id)
            .join(Language, Language.id == IngredientTranslation.language_id)
            .where(
                IngredientTranslation.name == normalized,
                Language.code == language_code,
            )
        )
        return self._one_or_none(statement)

    def add(self, ingredient: Ingredient) -> Ingredient:
        self.session.add(ingredient)
        self.session.flush()
        return ingredient
