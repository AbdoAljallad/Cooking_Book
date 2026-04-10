from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemeColors:
    background: str
    surface: str
    surface_alt: str
    text_primary: str
    text_secondary: str
    accent: str
    accent_hover: str
    border: str


@dataclass(frozen=True, slots=True)
class ThemeSpacing:
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32


@dataclass(frozen=True, slots=True)
class ThemeRadii:
    sm: int = 8
    md: int = 14
    lg: int = 22


@dataclass(frozen=True, slots=True)
class ThemeTypography:
    family_primary: str
    family_display: str
    size_body: int = 14
    size_caption: int = 12
    size_title: int = 18
    size_display: int = 28


@dataclass(frozen=True, slots=True)
class ThemeDefinition:
    name: str
    colors: ThemeColors
    spacing: ThemeSpacing
    radii: ThemeRadii
    typography: ThemeTypography
