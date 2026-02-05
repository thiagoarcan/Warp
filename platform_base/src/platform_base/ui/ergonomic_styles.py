"""
Ergonomic Styles - Sistema de estilos ergonômicos para UI profissional

Design Principles:
1. Hierarquia Visual Clara - Títulos, subtítulos e corpo distintos
2. Grid System 8px - Espaçamentos consistentes e respiração
3. Estados Interativos - Hover, focus, active bem definidos
4. Acessibilidade - Contraste WCAG AA, áreas de toque 44px
5. Micro-interações - Transições suaves para feedback
6. Densidade Adaptativa - Compacto mas legível

Baseado em Material Design 3 e Fluent Design System
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ErgonomicSpacing:
    """Sistema de espaçamento baseado em grid de 8px"""
    
    # Espaçamentos base
    xxs: int = 2   # micro gaps
    xs: int = 4    # tight
    sm: int = 8    # small - base unit
    md: int = 16   # medium - standard
    lg: int = 24   # large
    xl: int = 32   # extra large
    xxl: int = 48  # major sections
    
    # Componentes
    button_h_padding: int = 16
    button_v_padding: int = 8
    input_padding: int = 12
    card_padding: int = 16
    section_gap: int = 24
    panel_padding: int = 12


@dataclass
class ErgonomicTypography:
    """Sistema tipográfico com hierarquia clara"""
    
    # Font stack
    font_family: str = "'Segoe UI', 'SF Pro Display', -apple-system, system-ui, sans-serif"
    font_family_mono: str = "'Cascadia Code', 'Fira Code', 'Consolas', monospace"
    
    # Escala tipográfica (Major Third - 1.25)
    size_xs: int = 11    # labels secundários
    size_sm: int = 12    # captions
    size_base: int = 13  # corpo principal - otimizado para densidade
    size_md: int = 14    # ênfase
    size_lg: int = 16    # subtítulos
    size_xl: int = 18    # títulos de seção
    size_xxl: int = 22   # títulos principais
    size_display: int = 28  # display
    
    # Pesos
    weight_light: int = 300
    weight_regular: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    
    # Line heights
    line_height_tight: float = 1.2
    line_height_normal: float = 1.4
    line_height_relaxed: float = 1.6


@dataclass
class ErgonomicShadows:
    """Elevação e sombras para hierarquia z"""
    
    elevation_0: str = "none"
    elevation_1: str = "0 1px 2px rgba(0,0,0,0.1)"
    elevation_2: str = "0 2px 8px rgba(0,0,0,0.12)"
    elevation_3: str = "0 4px 16px rgba(0,0,0,0.14)"
    elevation_4: str = "0 8px 24px rgba(0,0,0,0.16)"
    
    # Sombras para estados
    focus_ring: str = "0 0 0 3px {primary_alpha}"  # com cor primária 30% opacidade


@dataclass
class ErgonomicBorders:
    """Bordas e raios"""
    
    radius_none: int = 0
    radius_sm: int = 4
    radius_md: int = 6
    radius_lg: int = 8
    radius_xl: int = 12
    radius_full: int = 9999  # pill shape
    
    width_thin: int = 1
    width_medium: int = 2
    width_thick: int = 3


@dataclass 
class ErgonomicAnimation:
    """Durações e curvas de animação"""
    
    duration_instant: str = "0ms"
    duration_fast: str = "100ms"
    duration_normal: str = "200ms"
    duration_slow: str = "300ms"
    duration_slower: str = "500ms"
    
    easing_default: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    easing_decelerate: str = "cubic-bezier(0, 0, 0.2, 1)"
    easing_accelerate: str = "cubic-bezier(0.4, 0, 1, 1)"


# Instâncias globais
SPACING = ErgonomicSpacing()
TYPOGRAPHY = ErgonomicTypography()
SHADOWS = ErgonomicShadows()
BORDERS = ErgonomicBorders()
ANIMATION = ErgonomicAnimation()


def generate_ergonomic_stylesheet(colors) -> str:
    """
    Gera stylesheet CSS ergonômico baseado nas cores do tema.
    
    Args:
        colors: ThemeColors object com as cores do tema atual
        
    Returns:
        String CSS completa
    """
    sp = SPACING
    ty = TYPOGRAPHY
    bd = BORDERS
    
    # Calcular cor primária com alpha para focus ring
    primary_rgb = _hex_to_rgb(colors.primary)
    primary_alpha = f"rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.3)"
    
    return f"""
/* ============================================================================
   ERGONOMIC STYLESHEET - Platform Base v2.0
   Professional UI with optimal ergonomics for engineering workflows
   ============================================================================ */

/* ===========================================================================
   RESET & BASE
   =========================================================================== */

* {{
    margin: 0;
    padding: 0;
}}

QWidget {{
    font-family: {ty.font_family};
    font-size: {ty.size_base}px;
    font-weight: {ty.weight_regular};
    line-height: {ty.line_height_normal};
    color: {colors.foreground};
    background-color: {colors.background};
}}

/* ===========================================================================
   TYPOGRAPHY HIERARCHY
   =========================================================================== */

/* Section Headers - Títulos de painéis */
QDockWidget::title,
QGroupBox::title {{
    font-size: {ty.size_lg}px;
    font-weight: {ty.weight_semibold};
    color: {colors.text_primary};
    letter-spacing: 0.3px;
}}

/* Labels principais */
QLabel {{
    font-size: {ty.size_base}px;
    color: {colors.text_primary};
    padding: 0;
}}

/* Labels secundários */
QLabel[secondary="true"] {{
    font-size: {ty.size_sm}px;
    color: {colors.text_secondary};
}}

/* Monospace para dados/valores */
QLabel[monospace="true"],
QLineEdit[monospace="true"] {{
    font-family: {ty.font_family_mono};
    font-size: {ty.size_sm}px;
}}

/* ===========================================================================
   BUTTONS - Touch-friendly (min 32px height)
   =========================================================================== */

QPushButton {{
    min-height: 32px;
    min-width: 80px;
    padding: {sp.button_v_padding}px {sp.button_h_padding}px;
    font-size: {ty.size_base}px;
    font-weight: {ty.weight_medium};
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_md}px;
    background-color: {colors.surface};
    color: {colors.text_primary};
}}

QPushButton:hover {{
    background-color: {colors.surface_variant};
    border-color: {colors.primary};
}}

QPushButton:focus {{
    outline: none;
    border-color: {colors.primary};
    box-shadow: 0 0 0 3px {primary_alpha};
}}

QPushButton:pressed {{
    background-color: {_darken(colors.surface_variant, 5)};
}}

QPushButton:disabled {{
    color: {colors.text_disabled};
    background-color: {colors.surface};
    border-color: {colors.border};
}}

/* Primary buttons - CTA */
QPushButton[primary="true"],
QPushButton#primaryButton {{
    background-color: {colors.primary};
    color: #FFFFFF;
    border: none;
    font-weight: {ty.weight_semibold};
}}

QPushButton[primary="true"]:hover,
QPushButton#primaryButton:hover {{
    background-color: {_darken(colors.primary, 8)};
}}

QPushButton[primary="true"]:pressed,
QPushButton#primaryButton:pressed {{
    background-color: {_darken(colors.primary, 15)};
}}

/* Success buttons */
QPushButton[success="true"] {{
    background-color: {colors.success};
    color: #FFFFFF;
    border: none;
}}

/* Danger buttons */
QPushButton[danger="true"] {{
    background-color: {colors.error};
    color: #FFFFFF;
    border: none;
}}

/* Icon-only buttons - compact */
QPushButton[icon-only="true"],
QToolButton {{
    min-width: 32px;
    min-height: 32px;
    padding: {sp.xs}px;
    border: none;
    background-color: transparent;
    border-radius: {bd.radius_sm}px;
}}

QToolButton:hover {{
    background-color: {colors.surface_variant};
}}

QToolButton:pressed {{
    background-color: {colors.border};
}}

/* ===========================================================================
   INPUT FIELDS - Clear focus states
   =========================================================================== */

QLineEdit,
QTextEdit,
QPlainTextEdit {{
    min-height: 32px;
    padding: {sp.xs}px {sp.sm}px;
    font-size: {ty.size_base}px;
    background-color: {colors.surface};
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_md}px;
    selection-background-color: {colors.primary};
    selection-color: #FFFFFF;
}}

QLineEdit:hover,
QTextEdit:hover,
QPlainTextEdit:hover {{
    border-color: {colors.secondary};
}}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus {{
    border-color: {colors.primary};
    border-width: {bd.width_medium}px;
    background-color: {colors.background};
}}

QLineEdit:disabled,
QTextEdit:disabled,
QPlainTextEdit:disabled {{
    background-color: {colors.surface};
    color: {colors.text_disabled};
}}

/* Search input with icon */
QLineEdit#searchInput {{
    padding-left: 32px;
    border-radius: {bd.radius_lg}px;
}}

/* ===========================================================================
   SPINBOX & NUMBER INPUTS
   =========================================================================== */

QSpinBox,
QDoubleSpinBox {{
    min-height: 32px;
    min-width: 80px;
    padding: {sp.xs}px {sp.sm}px;
    padding-right: 24px;
    font-family: {ty.font_family_mono};
    font-size: {ty.size_base}px;
    background-color: {colors.surface};
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_md}px;
}}

QSpinBox:focus,
QDoubleSpinBox:focus {{
    border-color: {colors.primary};
    border-width: {bd.width_medium}px;
}}

QSpinBox::up-button,
QSpinBox::down-button,
QDoubleSpinBox::up-button,
QDoubleSpinBox::down-button {{
    width: 20px;
    border: none;
    background-color: transparent;
}}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover,
QDoubleSpinBox::down-button:hover {{
    background-color: {colors.surface_variant};
}}

/* ===========================================================================
   COMBOBOX - Dropdown selects
   =========================================================================== */

QComboBox {{
    min-height: 32px;
    min-width: 100px;
    padding: {sp.xs}px {sp.sm}px;
    padding-right: 28px;
    font-size: {ty.size_base}px;
    background-color: {colors.surface};
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_md}px;
}}

QComboBox:hover {{
    border-color: {colors.secondary};
}}

QComboBox:focus {{
    border-color: {colors.primary};
    border-width: {bd.width_medium}px;
}}

QComboBox::drop-down {{
    width: 24px;
    border: none;
    border-left: 1px solid {colors.border};
    background-color: transparent;
}}

QComboBox QAbstractItemView {{
    background-color: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: {bd.radius_sm}px;
    padding: {sp.xs}px;
    selection-background-color: {colors.primary};
    selection-color: #FFFFFF;
}}

QComboBox QAbstractItemView::item {{
    min-height: 28px;
    padding: {sp.xs}px {sp.sm}px;
    border-radius: {bd.radius_sm}px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {colors.surface_variant};
}}

/* ===========================================================================
   CHECKBOX & RADIO - Accessible sizing
   =========================================================================== */

QCheckBox,
QRadioButton {{
    spacing: {sp.sm}px;
    min-height: 28px;
    font-size: {ty.size_base}px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: {bd.width_medium}px solid {colors.border};
    border-radius: {bd.radius_sm}px;
    background-color: {colors.surface};
}}

QCheckBox::indicator:hover {{
    border-color: {colors.primary};
}}

QCheckBox::indicator:checked {{
    background-color: {colors.primary};
    border-color: {colors.primary};
}}

QCheckBox::indicator:disabled {{
    background-color: {colors.surface_variant};
    border-color: {colors.border};
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: {bd.width_medium}px solid {colors.border};
    border-radius: 10px;
    background-color: {colors.surface};
}}

QRadioButton::indicator:hover {{
    border-color: {colors.primary};
}}

QRadioButton::indicator:checked {{
    background-color: {colors.primary};
    border-color: {colors.primary};
}}

/* ===========================================================================
   SLIDERS - Touch-friendly handles
   =========================================================================== */

QSlider {{
    min-height: 32px;
}}

QSlider::groove:horizontal {{
    height: 6px;
    background-color: {colors.border};
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background-color: {colors.primary};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    width: 20px;
    height: 20px;
    margin: -7px 0;
    background-color: {colors.primary};
    border: 3px solid {colors.background};
    border-radius: 10px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {_darken(colors.primary, 10)};
    transform: scale(1.1);
}}

QSlider::handle:horizontal:pressed {{
    background-color: {_darken(colors.primary, 20)};
}}

/* ===========================================================================
   PROGRESS BAR
   =========================================================================== */

QProgressBar {{
    height: 8px;
    background-color: {colors.surface_variant};
    border: none;
    border-radius: 4px;
    text-align: center;
    font-size: {ty.size_xs}px;
}}

QProgressBar::chunk {{
    background-color: {colors.primary};
    border-radius: 4px;
}}

/* Large progress */
QProgressBar[large="true"] {{
    height: 20px;
    font-size: {ty.size_sm}px;
}}

/* ===========================================================================
   LISTS, TREES, TABLES - Dense but readable
   =========================================================================== */

QListView,
QTreeView,
QTableView {{
    background-color: {colors.surface};
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_md}px;
    padding: {sp.xxs}px;
    alternate-background-color: {colors.surface_variant};
}}

QListView::item,
QTreeView::item {{
    min-height: 28px;
    padding: {sp.xs}px {sp.sm}px;
    border-radius: {bd.radius_sm}px;
    margin: 1px 2px;
}}

QListView::item:hover,
QTreeView::item:hover {{
    background-color: {colors.surface_variant};
}}

QListView::item:selected,
QTreeView::item:selected {{
    background-color: {colors.primary};
    color: #FFFFFF;
}}

QListView::item:selected:!active,
QTreeView::item:selected:!active {{
    background-color: {_fade(colors.primary, 50)};
    color: {colors.text_primary};
}}

/* Tree expansion indicator */
QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {{
    border-image: none;
}}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings {{
    border-image: none;
}}

/* Table headers */
QHeaderView::section {{
    background-color: {colors.surface};
    border: none;
    border-bottom: 1px solid {colors.border};
    border-right: 1px solid {colors.border};
    padding: {sp.sm}px;
    font-weight: {ty.weight_semibold};
    font-size: {ty.size_sm}px;
    color: {colors.text_secondary};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:hover {{
    background-color: {colors.surface_variant};
}}

/* ===========================================================================
   TABS - Clear active state
   =========================================================================== */

QTabWidget::pane {{
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_md}px;
    background-color: {colors.background};
    margin-top: -1px;
}}

QTabBar {{
    background-color: transparent;
}}

QTabBar::tab {{
    min-width: 100px;
    min-height: 36px;
    padding: {sp.sm}px {sp.md}px;
    font-size: {ty.size_base}px;
    font-weight: {ty.weight_medium};
    background-color: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    color: {colors.text_secondary};
}}

QTabBar::tab:hover {{
    color: {colors.text_primary};
    background-color: {colors.surface_variant};
}}

QTabBar::tab:selected {{
    color: {colors.primary};
    border-bottom-color: {colors.primary};
    background-color: transparent;
}}

/* ===========================================================================
   DOCK WIDGETS - Clean panels
   =========================================================================== */

QDockWidget {{
    font-size: {ty.size_base}px;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}}

QDockWidget::title {{
    background-color: {colors.surface};
    padding: {sp.sm}px {sp.md}px;
    border-bottom: 1px solid {colors.border};
    font-weight: {ty.weight_semibold};
    font-size: {ty.size_md}px;
    text-align: left;
}}

QDockWidget::close-button,
QDockWidget::float-button {{
    border: none;
    background-color: transparent;
    padding: {sp.xs}px;
    border-radius: {bd.radius_sm}px;
}}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {{
    background-color: {colors.surface_variant};
}}

/* ===========================================================================
   GROUPBOX - Section containers
   =========================================================================== */

QGroupBox {{
    background-color: {colors.surface};
    border: {bd.width_thin}px solid {colors.border};
    border-radius: {bd.radius_lg}px;
    margin-top: {sp.lg}px;
    padding: {sp.md}px;
    padding-top: {sp.lg}px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: {sp.md}px;
    padding: 0 {sp.sm}px;
    font-size: {ty.size_md}px;
    font-weight: {ty.weight_semibold};
    color: {colors.text_primary};
    background-color: {colors.surface};
}}

/* ===========================================================================
   SCROLLBARS - Minimal but functional
   =========================================================================== */

QScrollBar:vertical {{
    width: 10px;
    background-color: transparent;
    border: none;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors.border};
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors.secondary};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background-color: transparent;
}}

QScrollBar:horizontal {{
    height: 10px;
    background-color: transparent;
    border: none;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors.border};
    border-radius: 4px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors.secondary};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ===========================================================================
   SPLITTER - Visible resize handles
   =========================================================================== */

QSplitter {{
    background-color: transparent;
}}

QSplitter::handle {{
    background-color: {colors.border};
    border-radius: 2px;
}}

QSplitter::handle:hover {{
    background-color: {colors.primary};
}}

QSplitter::handle:pressed {{
    background-color: {_darken(colors.primary, 15)};
}}

QSplitter::handle:horizontal {{
    width: 5px;
    margin: 4px 0px;
}}

QSplitter::handle:vertical {{
    height: 5px;
    margin: 0px 4px;
}}

/* ===========================================================================
   MENU BAR & MENUS
   =========================================================================== */

QMenuBar {{
    background-color: {colors.background};
    border-bottom: 1px solid {colors.border};
    padding: {sp.xxs}px;
    font-size: {ty.size_base}px;
}}

QMenuBar::item {{
    padding: {sp.sm}px {sp.md}px;
    border-radius: {bd.radius_sm}px;
    background-color: transparent;
}}

QMenuBar::item:selected {{
    background-color: {colors.surface_variant};
}}

QMenuBar::item:pressed {{
    background-color: {colors.surface};
}}

QMenu {{
    background-color: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: {bd.radius_md}px;
    padding: {sp.xs}px;
}}

QMenu::item {{
    padding: {sp.sm}px {sp.lg}px;
    padding-right: {sp.xxl}px;
    border-radius: {bd.radius_sm}px;
    font-size: {ty.size_base}px;
}}

QMenu::item:selected {{
    background-color: {colors.primary};
    color: #FFFFFF;
}}

QMenu::item:disabled {{
    color: {colors.text_disabled};
}}

QMenu::separator {{
    height: 1px;
    background-color: {colors.border};
    margin: {sp.xs}px {sp.sm}px;
}}

QMenu::indicator {{
    width: 18px;
    height: 18px;
    margin-left: {sp.sm}px;
}}

/* ===========================================================================
   TOOLBAR - Clean action bar
   =========================================================================== */

QToolBar {{
    background-color: {colors.background};
    border-bottom: 1px solid {colors.border};
    padding: {sp.xs}px {sp.sm}px;
    spacing: {sp.xs}px;
}}

QToolBar::separator {{
    width: 1px;
    background-color: {colors.border};
    margin: {sp.xs}px {sp.sm}px;
}}

/* ===========================================================================
   STATUS BAR
   =========================================================================== */

QStatusBar {{
    background-color: {colors.surface};
    border-top: 1px solid {colors.border};
    padding: {sp.xs}px {sp.sm}px;
    font-size: {ty.size_sm}px;
    color: {colors.text_secondary};
}}

QStatusBar::item {{
    border: none;
}}

QStatusBar QLabel {{
    padding: 0 {sp.sm}px;
}}

/* ===========================================================================
   TOOLTIPS
   =========================================================================== */

QToolTip {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    border-radius: {bd.radius_sm}px;
    padding: {sp.sm}px {sp.md}px;
    font-size: {ty.size_sm}px;
}}

/* ===========================================================================
   DIALOGS
   =========================================================================== */

QDialog {{
    background-color: {colors.background};
}}

QDialog QLabel#titleLabel {{
    font-size: {ty.size_xl}px;
    font-weight: {ty.weight_bold};
    color: {colors.text_primary};
    padding-bottom: {sp.md}px;
}}

QDialogButtonBox {{
    button-layout: 3;
}}

QDialogButtonBox QPushButton {{
    min-width: 90px;
}}

/* ===========================================================================
   FRAME VARIANTS
   =========================================================================== */

QFrame {{
    border: none;
    background-color: transparent;
}}

QFrame[frameShape="4"] {{ /* HLine */
    background-color: {colors.border};
    max-height: 1px;
}}

QFrame[frameShape="5"] {{ /* VLine */
    background-color: {colors.border};
    max-width: 1px;
}}

/* Card-style frame */
QFrame[card="true"] {{
    background-color: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: {bd.radius_lg}px;
    padding: {sp.md}px;
}}

/* ===========================================================================
   SPECIAL PANELS
   =========================================================================== */

/* Data Panel - Lista de séries */
QWidget#dataPanel QTreeView {{
    font-size: {ty.size_sm}px;
}}

QWidget#dataPanel QTreeView::item {{
    min-height: 26px;
}}

/* Config Panel - Seções compactas */
QWidget#configPanel QGroupBox {{
    margin-top: {sp.md}px;
    padding: {sp.sm}px;
}}

/* Operations Panel - Botões de ação */
QWidget#operationsPanel QPushButton {{
    min-width: 120px;
}}

/* Results Panel - Tabela de resultados */
QWidget#resultsPanel QTableView {{
    gridline-color: {colors.border};
}}

/* Streaming Panel - Controles de playback */
QWidget#streamingPanel QSlider {{
    min-height: 24px;
}}

QWidget#streamingPanel QPushButton {{
    min-width: 40px;
    min-height: 40px;
    font-size: {ty.size_lg}px;
}}

/* ===========================================================================
   UTILITY CLASSES
   =========================================================================== */

/* Compact variant */
QWidget[compact="true"] QPushButton {{
    min-height: 28px;
    padding: {sp.xs}px {sp.sm}px;
}}

QWidget[compact="true"] QLineEdit,
QWidget[compact="true"] QComboBox {{
    min-height: 28px;
}}

/* Dense variant */
QWidget[dense="true"] {{
    font-size: {ty.size_sm}px;
}}

QWidget[dense="true"] QPushButton {{
    min-height: 24px;
    padding: {sp.xxs}px {sp.xs}px;
}}

/* Accent colors */
QWidget[accent="success"] {{
    color: {colors.success};
}}

QWidget[accent="warning"] {{
    color: {colors.warning};
}}

QWidget[accent="error"] {{
    color: {colors.error};
}}

QWidget[accent="info"] {{
    color: {colors.info};
}}

"""


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converte cor hex para RGB."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def _darken(hex_color: str, percent: int) -> str:
    """Escurece uma cor hex."""
    from PyQt6.QtGui import QColor
    color = QColor(hex_color)
    h, s, l, a = color.getHslF()
    if h is None or s is None or l is None or a is None:
        return hex_color
    l = max(0.0, l - percent / 100)
    color.setHslF(h, s, l, a)
    return color.name()


def _lighten(hex_color: str, percent: int) -> str:
    """Clareia uma cor hex."""
    from PyQt6.QtGui import QColor
    color = QColor(hex_color)
    h, s, l, a = color.getHslF()
    if h is None or s is None or l is None or a is None:
        return hex_color
    l = min(1.0, l + percent / 100)
    color.setHslF(h, s, l, a)
    return color.name()


def _fade(hex_color: str, percent: int) -> str:
    """Adiciona transparência a uma cor (retorna rgba)."""
    r, g, b = _hex_to_rgb(hex_color)
    alpha = percent / 100
    return f"rgba({r}, {g}, {b}, {alpha})"


__all__ = [
    'ANIMATION',
    'BORDERS', 
    'ErgonomicAnimation',
    'ErgonomicBorders',
    'ErgonomicShadows',
    'ErgonomicSpacing',
    'ErgonomicTypography',
    'SHADOWS',
    'SPACING',
    'TYPOGRAPHY',
    'generate_ergonomic_stylesheet',
]
