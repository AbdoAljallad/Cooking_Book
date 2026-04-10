from app.ui.themes.base import (
    ThemeColors,
    ThemeDefinition,
    ThemeRadii,
    ThemeSpacing,
    ThemeTypography,
)


DARK_THEME = ThemeDefinition(
    name="dark",
    colors=ThemeColors(
        background="#0F172A",
        surface="#111827",
        surface_alt="#1F2937",
        text_primary="#F8FAFC",
        text_secondary="#94A3B8",
        accent="#EAB308",
        accent_hover="#FACC15",
        border="#334155",
    ),
    spacing=ThemeSpacing(),
    radii=ThemeRadii(),
    typography=ThemeTypography(
        family_primary="Segoe UI",
        family_display="Segoe UI Semibold",
    ),
)

LIGHT_THEME = ThemeDefinition(
    name="light",
    colors=ThemeColors(
        background="#F8FAFC",
        surface="#FFFFFF",
        surface_alt="#E2E8F0",
        text_primary="#0F172A",
        text_secondary="#475569",
        accent="#B45309",
        accent_hover="#D97706",
        border="#CBD5E1",
    ),
    spacing=ThemeSpacing(),
    radii=ThemeRadii(),
    typography=ThemeTypography(
        family_primary="Segoe UI",
        family_display="Segoe UI Semibold",
    ),
)


BUILTIN_THEMES = {
    DARK_THEME.name: DARK_THEME,
    LIGHT_THEME.name: LIGHT_THEME,
}
