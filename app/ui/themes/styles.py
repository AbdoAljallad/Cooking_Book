from app.ui.themes.base import ThemeDefinition


def build_stylesheet(theme: ThemeDefinition) -> str:
    colors = theme.colors
    spacing = theme.spacing
    radii = theme.radii
    typography = theme.typography

    return f"""
    QWidget {{
        background-color: {colors.background};
        color: {colors.text_primary};
        font-family: "{typography.family_primary}";
        font-size: {typography.size_body}px;
    }}

    QMainWindow {{
        background-color: {colors.background};
    }}

    QLabel#heroTitle {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_display}px;
        font-weight: 600;
        color: {colors.text_primary};
    }}

    QLabel#heroSubtitle,
    QLabel#sectionSubtitle {{
        color: {colors.text_secondary};
        font-size: {typography.size_body}px;
    }}

    QLabel#sectionTitle {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_title}px;
        color: {colors.text_primary};
    }}

    QLabel#windowTitleLabel {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_title}px;
        color: {colors.text_primary};
    }}

    QLabel#brandLogo {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: {radii.lg}px;
        padding: {spacing.sm}px;
    }}

    QLabel#windowSubtitleLabel,
    QLabel#recipeCardMeta,
    QLabel#emptyStateDescription {{
        color: {colors.text_secondary};
    }}

    QLabel#eyebrowLabel {{
        color: {colors.accent};
        font-family: "{typography.family_display}";
        font-size: {typography.size_caption}px;
        font-weight: 700;
    }}

    QWidget#homePage,
    QScrollArea#pageScrollArea {{
        background: transparent;
    }}

    QFrame#baseCard {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: {radii.lg}px;
    }}

    QFrame#heroCard {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: {radii.lg}px;
    }}

    QWidget#sideNav {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: {radii.lg}px;
    }}

    QLabel#navSectionLabel {{
        color: {colors.text_secondary};
        font-family: "{typography.family_display}";
        font-size: {typography.size_caption}px;
        font-weight: 700;
        padding: {spacing.sm}px {spacing.md}px;
    }}

    QPushButton#navButton {{
        background-color: transparent;
        color: {colors.text_secondary};
        border: 1px solid transparent;
        border-radius: {radii.md}px;
        min-height: 42px;
        padding: 0 {spacing.md}px;
        text-align: left;
        font-weight: 700;
    }}

    QPushButton#navButton:hover {{
        color: {colors.text_primary};
        background-color: {colors.surface_alt};
        border-color: {colors.border};
    }}

    QPushButton#navButton[active="true"] {{
        color: {colors.background};
        background-color: {colors.accent};
        border-color: {colors.accent};
    }}

    QFrame#imageDropCard {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: {radii.lg}px;
    }}

    QFrame#imageDropCard[dropActive="true"] {{
        border: 2px dashed {colors.accent};
        background-color: rgba(250, 204, 21, 0.08);
    }}

    QFrame#detailsHeroCard {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: {radii.lg}px;
    }}

    QFrame#recipeCard {{
        min-height: 380px;
        max-width: 390px;
    }}

    QLabel#recipeCardTitle {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_title}px;
        color: {colors.text_primary};
    }}

    QLabel#recipeCardDescription {{
        color: {colors.text_secondary};
    }}

    QLabel#detailsTitle {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_display}px;
        color: {colors.text_primary};
    }}

    QLabel#detailLinePrimary {{
        color: {colors.text_primary};
        font-size: {typography.size_body}px;
    }}

    QLabel#detailLineSecondary,
    QLabel#detailMetaLabel {{
        color: {colors.text_secondary};
    }}

    QLabel#detailMetaValue {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_title}px;
        color: {colors.text_primary};
    }}

    QWidget#detailMetaChip {{
        background-color: {colors.surface_alt};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
    }}

    QLabel#recipeImage {{
        background-color: {colors.surface_alt};
        border: 1px dashed {colors.border};
        border-radius: {radii.md}px;
        color: {colors.text_secondary};
        padding: 0px;
    }}

    QWidget#searchBar {{
        background-color: transparent;
    }}

    QLineEdit#searchInput,
    QComboBox#comboField,
    QSpinBox#spinField,
    QDoubleSpinBox#spinField {{
        background-color: {colors.surface_alt};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        padding: {spacing.md}px {spacing.lg}px;
        min-height: 24px;
        selection-background-color: {colors.accent};
        selection-color: {colors.background};
    }}

    QTextEdit#multilineField {{
        background-color: {colors.surface_alt};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        padding: {spacing.md}px;
    }}

    QPushButton#secondaryButton,
    QPushButton#categoryChip {{
        background-color: {colors.surface_alt};
        color: {colors.text_primary};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        min-height: 40px;
        padding: 0 {spacing.lg}px;
        font-weight: 600;
    }}

    QPushButton#secondaryButton:hover,
    QPushButton#categoryChip:hover {{
        border-color: {colors.accent};
    }}

    QPushButton#secondaryButton[active="true"] {{
        background-color: rgba(250, 204, 21, 0.14);
        color: #FACC15;
        border-color: #A16207;
    }}

    QPushButton#categoryChip:checked {{
        background-color: {colors.accent};
        color: {colors.background};
        border-color: {colors.accent};
    }}

    QLabel#tagPill {{
        background-color: {colors.surface_alt};
        color: {colors.text_secondary};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        padding: {spacing.sm}px {spacing.md}px;
        font-weight: 600;
    }}

    QWidget#editorRow {{
        background-color: {colors.surface_alt};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        padding: {spacing.md}px;
    }}

    QWidget#ratingControl {{
        background-color: transparent;
    }}

    QPushButton#ratingStar {{
        background-color: {colors.surface_alt};
        color: {colors.text_secondary};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        min-width: 36px;
        min-height: 36px;
        font-size: {typography.size_title}px;
        font-weight: 700;
    }}

    QPushButton#ratingStar[active="true"] {{
        color: #FACC15;
        border-color: #A16207;
        background-color: rgba(250, 204, 21, 0.14);
    }}

    QPushButton#ratingStar:hover {{
        border-color: {colors.accent};
    }}

    QLabel#formErrorBanner {{
        background-color: rgba(249, 115, 22, 0.12);
        color: #F97316;
        border: 1px solid #7C2D12;
        border-radius: {radii.md}px;
        padding: {spacing.md}px;
        font-weight: 600;
    }}

    QWidget#emptyState {{
        background-color: {colors.surface};
        border: 1px dashed {colors.border};
        border-radius: {radii.lg}px;
    }}

    QLabel#emptyStateTitle {{
        font-family: "{typography.family_display}";
        font-size: {typography.size_title}px;
        color: {colors.text_primary};
    }}

    QPushButton#primaryButton {{
        background-color: {colors.accent};
        color: {colors.background};
        border: none;
        border-radius: {radii.md}px;
        min-height: 44px;
        padding: 0 {spacing.lg}px;
        font-weight: 600;
    }}

    QPushButton#primaryButton:hover {{
        background-color: {colors.accent_hover};
    }}

    QComboBox {{
        background-color: {colors.surface_alt};
        border: 1px solid {colors.border};
        border-radius: {radii.md}px;
        padding: {spacing.sm}px {spacing.md}px;
        min-height: 20px;
    }}

    QLabel#statusBadge {{
        border-radius: {radii.md}px;
        padding: {spacing.sm}px {spacing.md}px;
        font-weight: 600;
        border: 1px solid {colors.border};
        background-color: {colors.surface_alt};
    }}

    QLabel#statusBadge[status="checking"] {{
        color: {colors.text_secondary};
    }}

    QLabel#statusBadge[status="success"] {{
        color: #22C55E;
        border: 1px solid #14532D;
        background-color: rgba(34, 197, 94, 0.12);
    }}

    QLabel#statusBadge[status="error"] {{
        color: #F97316;
        border: 1px solid #7C2D12;
        background-color: rgba(249, 115, 22, 0.12);
    }}

    QLabel#statusDetails {{
        color: {colors.text_secondary};
    }}
    """
