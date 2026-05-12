"""
ThemeManager - Centralized theme management for ERP Medical Application.
Handles theme switching, color management, and stylesheet generation.
No dark colors - clean medical professional design.
"""

from typing import Optional, Callable
from ..utils.qt_compat import QtWidgets, QtCore, QtGui
from .theme_definitions import (
    ThemeType,
    ColorPalette,
    THEME_REGISTRY,
    LIGHT_PALETTE,
)


class ThemeManager(QtCore.QObject):
    """
    Centralized theme manager for the application.
    
    Usage:
        theme_manager = ThemeManager()
        theme_manager.apply_theme(app, ThemeType.LIGHT)
        
        # Listen for theme changes
        theme_manager.theme_changed.connect(on_theme_changed)
        
        # Switch theme at runtime
        theme_manager.set_theme(ThemeType.BLUE_WHITE)
    """
    
    # Signals
    theme_changed = QtCore.Signal(ThemeType)  # Emitted when theme changes
    
    def __init__(self, default_theme: ThemeType = ThemeType.LIGHT):
        """Initialize theme manager with default theme."""
        super().__init__()
        self._current_theme: ThemeType = default_theme
        self._palette: ColorPalette = THEME_REGISTRY[default_theme]
        self._app = None
        self._theme_change_callbacks = []
    
    @property
    def current_theme(self) -> ThemeType:
        """Get current theme."""
        return self._current_theme
    
    @property
    def palette(self) -> ColorPalette:
        """Get current color palette."""
        return self._palette
    
    def set_theme(self, theme: ThemeType):
        """
        Change the application theme and apply it to all widgets.
        
        Args:
            theme: ThemeType to switch to
        """
        if theme == self._current_theme:
            return  # No change needed
        
        self._current_theme = theme
        self._palette = THEME_REGISTRY[theme]
        
        # Apply theme to app if it's initialized
        if self._app:
            self._apply_stylesheet_to_app()
        
        # Notify all listeners
        self.theme_changed.emit(theme)
        for callback in self._theme_change_callbacks:
            callback(theme)
    
    def apply_theme(self, app, theme: Optional[ThemeType] = None):
        """
        Apply theme to the entire application.
        
        Args:
            app: QApplication instance
            theme: ThemeType to apply (uses current if None)
        """
        self._app = app
        
        if theme:
            self.set_theme(theme)
        else:
            self._apply_stylesheet_to_app()
    
    def _apply_stylesheet_to_app(self):
        """Apply current theme stylesheet to app."""
        if not self._app:
            return
        
        # Determine current role primary color if possible
        role_primary = None
        try:
            from .app import SmartMedicalApp
            app_instance = SmartMedicalApp.get_instance()
            if app_instance and app_instance.current_user:
                role = app_instance.current_role()
                role_primary = self.get_role_color(role)
        except Exception:
            pass

        stylesheet = self.generate_stylesheet(role_primary)
        self._app.setStyleSheet(stylesheet)
    
    def register_callback(self, callback: Callable[[ThemeType], None]):
        """
        Register a callback to be called when theme changes.
        
        Args:
            callback: Function(theme_type) to call on theme change
        """
        self._theme_change_callbacks.append(callback)
    
    def generate_stylesheet(self, role_primary: str = None) -> str:
        """
        Generate complete stylesheet for current palette.
        
        Args:
            role_primary: Optional hex color to override primary accent (for RBAC coloring)
            
        Returns:
            Complete QSS stylesheet string
        """
        p = self._palette
        # Use role color if provided, else use theme primary
        primary = role_primary if role_primary else p.primary
        
        stylesheet = f"""
/* ============================================================================
   ERP MEDICAL APPLICATION - THEME STYLESHEET (STABILIZED FULL LIGHT)
   ============================================================================ */

/* === GLOBAL STYLES === */
* {{
    color: {p.text_primary};
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    outline: none;
}}

QMainWindow, QDialog, QWidget#central_widget, QWidget#content_area_container, QStackedWidget#content_area, QWidget#main_container_widget, QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: {p.background};
    border: none;
}}

QLabel {{
    background-color: transparent;
    color: {p.text_primary};
}}

/* Labels for login dialog */
QDialog#login_dialog QLabel,
QDialog#login_dialog QLabel#login_title,
QDialog#login_dialog QLabel#login_subtitle,
QDialog#login_dialog QLabel#login_icon {{
    color: {primary};
}}

/* === PANELS & FRAMES (FORCE WHITE) === */
QFrame#nav_panel {{
    background-color: white;
    border-right: 1px solid {p.border_light};
}}

QFrame#logo_frame {{
    border: none;
    background-color: transparent;
}}

QLabel#logo_name {{
    color: {primary};
    font-size: 16pt;
    font-weight: bold;
}}

QLabel#logo_icon {{
    color: {primary};
    font-size: 18pt;
}}

QLabel#role_badge {{
    background-color: #e6f7ff;
    color: #1890ff;
    font-size: 8pt;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 12px;
    margin: 0 20px;
}}

QFrame#profile_card {{
    background-color: white;
    border-top: 1px solid #e1e4e8;
}}

QLabel#profile_name {{
    color: #0050b3;
    font-weight: bold;
}}

QLabel#profile_role {{
    color: #1890ff;
    font-size: 9pt;
}}

QFrame#header_bar {{
    background-color: {p.surface_light};
    border-bottom: 1px solid {p.border};
}}

QFrame.stat_card {{
    background-color: {p.surface_light};
    border: 1px solid {p.border_light};
    border-radius: 16px;
}}

QFrame#container {{
    background-color: {p.background};
}}

/* === DASHBOARD PANELS === */
QFrame#wait_panel, QFrame#apt_panel, QFrame#qa_panel, QFrame#ai_panel, QFrame.card, QFrame.stat_card, QFrame#frame_stats, QFrame#frame_rdv_list, QFrame#frame_calendar {{
    background-color: white;
    border: 1px solid {p.border_light};
    border-radius: 12px;
}}

QFrame#wait_panel:hover, QFrame#apt_panel:hover, QFrame.card:hover {{
    border: 1px solid {p.primary_light};
    background-color: {p.surface_light};
}}

QFrame.card_accent {{
    background-color: {p.primary_very_light};
    border: 1px solid {p.primary_light};
    border-radius: 16px;
    padding: 20px;
}}

QListWidget {{
    background-color: white;
    border: none;
    outline: none;
    border-radius: 8px;
}}

QListWidget::item {{
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 5px;
}}

QListWidget::item:hover {{
    background-color: {p.primary_very_light};
}}

QListWidget::item:selected {{
    background-color: {primary};
    color: white;
}}

/* === LOGIN SCREEN === */
QLabel#login_title {{
    font-size: 36pt;
    font-weight: 800;
    color: {primary};
    letter-spacing: -1px;
}}

QLabel#login_subtitle {{
    font-size: 13pt;
    color: {p.text_secondary};
    font-weight: 400;
}}

QLabel#login_icon {{
    font-size: 60pt;
    color: {primary};
    margin-bottom: 10px;
}}

QFrame#MainContainer {{
    background-color: {p.surface_light};
    border-radius: 40px;
    border: 1px solid {p.border_light};
}}

QLabel#lbl_welcome {{
    font-size: 16pt;
    font-weight: 600;
    color: {p.text_primary};
}}

QLineEdit#main_search {{
    background-color: #ffffff;
    border: 1px solid {p.primary_light};
    border-radius: 19px;
    padding-left: 15px;
    color: {primary};
}}

QLabel#header_title {{
    font-size: 20pt;
    font-weight: bold;
    color: {p.text_primary};
}}

QLabel#lblLogo {{
    color: {primary};
    font-size: 18pt;
    font-weight: bold;
}}

QLabel#card_title {{
    color: {p.text_secondary};
    font-size: 10pt;
}}

QLabel#card_value {{
    color: {p.text_primary};
    font-size: 20pt;
    font-weight: bold;
}}

/* === BUTTONS === */
QPushButton {{
    background-color: transparent;
    color: {p.text_primary};
    border: none;
    border-radius: 6px;
    padding: 10px 15px;
    font-size: 11pt;
}}

QPushButton:hover {{
    background-color: {p.primary_very_light};
    color: {primary};
}}

QPushButton:pressed {{
    background-color: {p.primary_light};
    color: white;
}}

QPushButton#btnPrimary {{
    background-color: #1890ff;
    color: white;
    font-weight: bold;
    font-size: 11pt;
    border-radius: 8px;
}}

QPushButton#btnPrimary:hover {{
    background-color: {p.primary_light};
    transform: translateY(-2px);
}}

QPushButton#btnPrimary:pressed {{
    background-color: {p.primary_dark};
}}

QPushButton#btnSecondary {{
    background-color: #e6f7ff;
    color: #1890ff;
    border: 1px solid #1890ff;
    font-weight: bold;
    font-size: 11pt;
    border-radius: 8px;
}}

QPushButton#btnSecondary:hover {{
    background-color: {p.primary_very_light};
    border-color: {primary};
}}

QPushButton#btnSuccess {{
    background-color: {p.success};
    color: white;
    font-weight: bold;
}}

QPushButton#btnSuccess:hover {{
    background-color: {p.success};
    opacity: 0.8;
}}

QPushButton#btnDanger {{
    background-color: {p.danger};
    color: white;
    font-weight: bold;
}}

QPushButton#btnDanger:hover {{
    background-color: {p.danger};
    opacity: 0.8;
}}

QPushButton#btnWarning {{
    background-color: {p.warning};
    color: white;
    font-weight: bold;
}}

QPushButton#btnWarning:hover {{
    background-color: {p.warning};
    opacity: 0.8;
}}

/* === SIDEBAR BUTTONS === */
QPushButton[nav_button="true"] {{
    text-align: left;
    padding: 15px 25px;
    background-color: white;
    border: none;
    color: #0050b3;
    border-radius: 8px;
    margin: 4px 12px;
}}

QPushButton[nav_button="true"]:hover {{
    background-color: #f5f6f8;
    color: #1890ff;
}}

QPushButton[nav_button="true"]:checked {{
    background-color: {primary};
    color: white;
    font-weight: bold;
    border: none;
}}

/* === TEXT INPUTS === */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
    background-color: white;
    color: {p.text_primary};
    border: 1px solid {p.border_light};
    border-radius: 8px;
    padding: 12px 18px;
    font-size: 12pt;
    min-height: 25px;
    selection-background-color: {primary};
    selection-color: white;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border: 2px solid {primary};
    background-color: white;
    color: #1890ff;
}}

/* Placeholders */
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: #8c8c8c;
    font-style: italic;
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
}}

/* Style the popup list */
QComboBox QAbstractItemView {{
    background-color: white;
    color: {p.text_primary};
    selection-background-color: {p.primary_very_light};
    selection-color: {primary};
    border: 1px solid {p.border};
    outline: none;
}}

/* === SPINBOX & SLIDER === */
QSpinBox, QDoubleSpinBox {{
    background-color: {p.background};
    color: {p.text_primary};
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 8px 12px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {primary};
}}

QSlider::handle:horizontal {{
    background-color: {primary};
    border: 1px solid {primary};
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::sub-page:horizontal {{
    background-color: {p.primary_very_light};
}}

/* === CHECKBOX & RADIO === */
QCheckBox, QRadioButton {{
    color: {p.text_primary};
    spacing: 5px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {p.border};
    border-radius: 3px;
    background-color: {p.background};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border: 1px solid {primary};
    background-color: {p.primary_very_light};
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {primary};
    border: 1px solid {primary};
}}

/* === TABLES & LISTS === */
QTableWidget, QListWidget, QTreeView, QListView, QHeaderView {{
    background-color: white;
    color: {p.text_primary};
    border: 1px solid {p.border};
    border-radius: 12px;
    gridline-color: {p.divider};
    alternate-background-color: #f9fbff;
    outline: none;
    font-size: 10pt;
}}

QHeaderView::section {{
    background-color: #f8fbff;
    color: {p.text_primary};
    padding: 12px;
    border: none;
    border-bottom: 2px solid {primary};
    font-weight: bold;
}}

QTableWidget::item, QListWidget::item, QTreeView::item {{
    padding: 12px;
    color: {p.text_primary};
    border-bottom: 1px solid {p.divider};
}}

QTableWidget::item:selected, QListWidget::item:selected, QTreeView::item:selected {{
    background-color: {p.primary_very_light};
    color: {primary};
    font-weight: bold;
}}

QHeaderView::section {{
    background-color: {p.surface_light};
    color: {p.text_primary};
    padding: 8px;
    border: none;
    border-bottom: 2px solid {primary};
    font-weight: bold;
}}

/* === TREEVIEW === */
QTreeView {{
    background-color: {p.background};
    color: {p.text_primary};
    border: 1px solid {p.border_light};
    alternate-background-color: {p.surface_light};
}}

QTreeView::item:selected {{
    background-color: {p.primary_very_light};
}}

/* === SCROLLBAR === */
QScrollBar:vertical {{
    background-color: {p.surface_light};
    width: 12px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background-color: {p.border};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {primary};
}}

QScrollBar:horizontal {{
    background-color: {p.surface_light};
    height: 12px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background-color: {p.border};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {primary};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    border: none;
    background: none;
}}

/* === TABS === */
QTabWidget::pane {{
    border: 1px solid {p.border_light};
}}

QTabBar::tab {{
    background-color: {p.surface_light};
    color: {p.text_secondary};
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid {p.border_light};
}}

QTabBar::tab:selected {{
    background-color: {p.background};
    color: {primary};
    border-bottom: 2px solid {primary};
}}

QTabBar::tab:hover {{
    background-color: {p.surface};
}}

/* === MENUBAR & MENU === */
QMenuBar {{
    background-color: {p.background};
    color: {p.text_primary};
    border-bottom: 1px solid {p.border_light};
}}

QMenuBar::item:selected {{
    background-color: {p.primary_very_light};
}}

QMenu {{
    background-color: white;
    color: {p.text_primary};
    border: 1px solid {p.border};
}}

QMenu::item:selected {{
    background-color: {p.primary_very_light};
    color: {primary};
}}

/* === PROGRESSBAR === */
QProgressBar {{
    border: 1px solid {p.border};
    border-radius: 5px;
    background-color: {p.surface_light};
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {primary};
    border-radius: 3px;
}}

/* === STATUSBAR === */
QStatusBar {{
    background-color: {p.surface};
    border-top: 1px solid {p.border_light};
}}

/* === DOCKWIDGET === */
QDockWidget {{
    background-color: {p.background};
    titlebar-close-icon: none;
}}

QDockWidget::title {{
    background-color: {p.surface_light};
    padding: 5px;
}}

/* === TOOLTIPS === */
QToolTip {{
    background-color: white;
    color: #0050b3;
    border: 1px solid #e1e4e8;
    border-radius: 4px;
    padding: 5px 10px;
}}

/* === DIALOGS === */
QMessageBox {{
    background-color: {p.background};
}}

QMessageBox QLabel {{
    color: {p.text_primary};
}}

/* === CUSTOM CLASSES === */
QLabel.header {{
    font-size: 16pt;
    font-weight: bold;
    color: {p.text_primary};
}}

QLabel.section {{
    font-size: 12pt;
    font-weight: bold;
    color: {p.text_secondary};
}}

QLabel.subtitle {{
    font-size: 10pt;
    color: {p.text_tertiary};
}}

/* === SUCCESS STATE === */
.success {{
    background-color: {p.success_light};
    color: {p.success};
}}

/* === WARNING STATE === */
.warning {{
    background-color: {p.warning_light};
    color: {p.warning};
}}

/* === DANGER STATE === */
.danger {{
    background-color: {p.danger_light};
    color: {p.danger};
}}

/* === INFO STATE === */
.info {{
    background-color: {p.info_light};
    color: {p.info};
}}

/* === TEXT STATES === */
.success_text {{
    color: {p.success};
}}

.danger_text {{
    color: {p.danger};
}}

.warning_text {{
    color: {p.warning};
}}

.primary_text {{
    color: {primary};
}}

.secondary_text {{
    color: {p.text_secondary};
}}

QLabel#login_status {{
    font-size: 10pt;
    font-weight: 600;
    margin-top: 10px;
}}
QLineEdit#search_bar, QLineEdit#dlg_input, QComboBox#dlg_input {{
    background-color: white;
    color: {p.text_primary};
    border: 2px solid {p.border};
    border-radius: 8px;
    padding: 8px 12px;
}}

QTableWidget#user_table {{
    background-color: white;
    color: {p.text_primary};
    border: 1px solid {p.border};
    border-radius: 12px;
}}

QWidget#dialog_white, QDialog#dialog_white {{
    background-color: {p.surface};
}}

QLabel#dialog_title {{
    font-size: 13pt;
    font-weight: bold;
    color: {p.text_primary};
}}

QLabel#dialog_subtitle, QLabel#dialog_guide, QLabel#ai_text, .subtitle_text {{
    color: {p.text_secondary};
    font-size: 11pt;
}}

.header_text {{
    font-size: 22pt;
    font-weight: bold;
    color: {primary};
}}

.section_title {{
    font-size: 14pt;
    font-weight: 600;
    color: {p.text_primary};
    margin-bottom: 10px;
}}

QFrame#divider_line {{
    background-color: {p.border_light};
    min-height: 1px;
}}

QLabel#bio_status {{
    color: {p.text_secondary};
    font-size: 9pt;
}}

QPushButton#btnEnroll {{
    background-color: {p.primary_very_light};
    color: {primary};
    border: 1px solid {p.border};
    border-radius: 6px;
    font-weight: bold;
}}

/* === PATIENT PORTAL SPECIFICS === */
QFrame#patient_card_warning {{
    background-color: {p.warning_light};
    border: 1px solid {p.warning};
    border-radius: 20px;
}}

QPushButton#btnPatientAction {{
    background-color: white; 
    border: 2px solid {p.role_patient}; 
    border-radius: 12px; 
    color: {p.role_patient}; 
    font-weight: 600;
    font-size: 11pt;
}}

QPushButton#btnPatientAction:hover {{
    background-color: {p.role_patient}; 
    color: white;
}}

/* Additional view object rules */
QLabel#logo_icon, QLabel#logo_name {{
    color: {primary};
    background: transparent;
}}

QWidget#central_widget {{
    background-color: {p.background};
}}

QLabel#lbl_welcome {{
    font-size: 14pt;
    font-weight: 600;
    color: {p.text_primary};
}}

QLineEdit#main_search {{
    background: {p.surface_light};
    border: 1px solid {p.border_light};
    border-radius: 19px;
    padding: 0 15px;
    color: {p.text_secondary};
}}

QFrame#profile_card {{
    background-color: {p.surface_light};
}}

QLabel#profile_name {{
    font-weight: 600;
    font-size: 9pt;
    color: {p.text_primary};
}}

QLabel#profile_role {{
    font-size: 8pt;
    color: {p.text_secondary};
}}

QLabel#role_badge {{
    background-color: #fafafa;
    padding-left: 12px;
}}

QLabel#video_label {{
    background-color: {p.surface_light};
    border-radius: 12px;
    color: {primary};
}}

QLabel#status_label {{
    font-weight: bold;
    color: {primary};
    padding: 10px;
}}

QLabel#kpi_title {{
    font-size: 9pt; color: {p.text_secondary}; font-weight: 500;
}}

QLabel#kpi_icon {{
    font-size: 14pt; color: {primary};
}}

QLabel#kpi_value {{
    font-size: 24pt; font-weight: bold; color: {primary};
}}

QLabel#kpi_sub {{
    font-size: 8pt; color: {p.text_tertiary};
}}

QWidget#appointment_item {{
    background-color: white; border-radius: 10px; border: 1px solid {p.surface_light};
}}

QLabel#appt_time {{
    font-weight: bold; color: {p.text_primary}; min-width: 50px;
}}

QLabel#appt_name {{
    font-weight: 600; color: {p.text_primary};
}}

QLabel#appt_reason {{
    color: {p.text_secondary}; font-size: 9pt;
}}

QPushButton#btnLogout {{
    background-color: white; color: #0050b3; text-align: left; padding-left: 20px; font-size: 10pt; border: none;
}}

QPushButton#btnLogout:hover {{
    color: {p.danger}; background-color: #fff1f0;
}}

QPushButton#btnRegisterLink {{
    color: {primary};
    border: none;
    background: transparent;
    font-size: 9pt;
}}

QPushButton#btnRegisterLink:hover {{
    color: {p.primary_light};
    text-decoration: underline;
}}

/* === MESSAGES VIEW SPECIFICS === */
QFrame#messages_left, QFrame#messages_right {{
    background-color: white;
    border-radius: 16px;
    border: 1px solid {p.border_light};
}}

QLabel#messages_title, QLabel#msg_subject {{
    font-size: 18pt;
    font-weight: bold;
    color: {p.text_primary};
}}

QLabel#msg_meta, QLabel#reply_label {{
    color: {p.text_secondary};
    font-size: 10pt;
}}

QTextEdit#msg_body, QTextEdit#txt_reply {{
    background-color: #f8fafc;
    border: 1px solid {p.border_light};
    border-radius: 12px;
    color: {p.text_primary};
    padding: 10px;
}}

QFrame#msg_separator {{
    background-color: {p.divider};
    max-height: 1px;
}}
"""
        return stylesheet
    
    def get_role_color(self, role: str) -> str:
        """
        Get color for a specific user role.
        
        Args:
            role: Role name (ADMIN, DOCTOR, SECRETARY, ASSISTANT, PATIENT)
        
        Returns:
            Hex color code for the role
        """
        role_colors = {
            "ADMIN": self._palette.role_admin,
            "DOCTOR": self._palette.role_doctor,
            "SECRETARY": self._palette.role_secretary,
            "ASSISTANT": self._palette.role_assistant,
            "PATIENT": self._palette.role_patient,
        }
        return role_colors.get(role, self._palette.text_primary)
    
    def get_semantic_color(self, semantic_type: str) -> str:
        """
        Get semantic color (success, warning, danger, info).
        
        Args:
            semantic_type: Color type (success, warning, danger, info)
        
        Returns:
            Hex color code
        """
        colors = {
            "success": self._palette.success,
            "warning": self._palette.warning,
            "danger": self._palette.danger,
            "info": self._palette.info,
        }
        return colors.get(semantic_type, self._palette.text_primary)
    
    def get_semantic_light_color(self, semantic_type: str) -> str:
        """
        Get light semantic color (for backgrounds).
        
        Args:
            semantic_type: Color type (success, warning, danger, info)
        
        Returns:
            Hex color code (light background)
        """
        colors = {
            "success": self._palette.success_light,
            "warning": self._palette.warning_light,
            "danger": self._palette.danger_light,
            "info": self._palette.info_light,
        }
        return colors.get(semantic_type, self._palette.surface_light)


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get or create global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(ThemeType.LIGHT)
    return _theme_manager


def initialize_theme_manager(app, theme: ThemeType = ThemeType.LIGHT):
    """
    Initialize the global theme manager and apply theme to app.
    
    Args:
        app: QApplication instance
        theme: Initial theme to use
    """
    global _theme_manager
    _theme_manager = ThemeManager(theme)
    _theme_manager.apply_theme(app, theme)
    return _theme_manager
