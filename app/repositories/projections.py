from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LocalizedCategory:
    id: int
    slug: str
    sort_order: int
    is_active: bool
    display_name: str
    language_code: str | None


@dataclass(frozen=True, slots=True)
class LocalizedUnit:
    id: int
    code: str
    symbol: str | None
    is_fractional: bool
    is_active: bool
    display_name: str
    abbreviation: str | None
    language_code: str | None


@dataclass(frozen=True, slots=True)
class LocalizedTag:
    id: int
    slug: str
    is_active: bool
    display_name: str
    language_code: str | None


@dataclass(frozen=True, slots=True)
class RecipeListItem:
    id: int
    title: str
    short_description: str | None
    category_slug: str
    category_name: str | None
    prep_time_minutes: int
    cook_time_minutes: int
    total_time_minutes: int
    base_servings: Decimal
    difficulty_level: str
    source_type: str
    image_path: str | None
    created_at: datetime
    updated_at: datetime
