from __future__ import annotations

from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RecipeSourceType(str, Enum):
    ORIGINAL = "original"
    IMPORTED = "imported"
    ADAPTED = "adapted"
