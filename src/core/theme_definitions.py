"""
Theme definitions for ERP Medical Application.
Clean, professional medical app with white/blue colors - NO DARK COLORS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class ThemeType(Enum):
    """Available themes for the application."""
    LIGHT = "light"
    BLUE_WHITE = "blue_white"


@dataclass
class ColorPalette:
    """Color palette for the application."""
    
    # === BASE COLORS (WHITE & LIGHT) ===
    background: str  # Main app background
    surface: str     # Secondary surface (panels, dialogs)
    surface_light: str  # Very light surface (hover states)
    
    # === BLUE COLORS (PRIMARY) ===
    primary: str     # Main action color
    primary_light: str  # Lighter primary for hover
    primary_dark: str   # Darker primary for active states
    primary_very_light: str  # Very light for backgrounds
    
    # === TEXT COLORS (NO BLACK - BLUE TONES) ===
    text_primary: str      # Main text (dark blue)
    text_secondary: str    # Secondary text (medium blue)
    text_tertiary: str     # Tertiary text (light blue)
    
    # === BORDERS & DIVIDERS ===
    border: str           # Default border
    border_light: str     # Light border
    divider: str          # Divider lines
    
    # === SEMANTIC COLORS (LIGHT TONES) ===
    success: str          # Success/green
    success_light: str    # Light success background
    warning: str          # Warning/orange
    warning_light: str    # Light warning background
    danger: str           # Danger/red
    danger_light: str     # Light danger background
    info: str             # Info/blue
    info_light: str       # Light info background
    
    # === ROLE-BASED COLORS (LIGHT PALETTE) ===
    role_admin: str       # Admin color
    role_doctor: str      # Doctor color
    role_secretary: str   # Secretary color
    role_assistant: str   # Assistant color
    role_patient: str     # Patient color


# ============================================================================
# LIGHT THEME - Modern Dashboard (Dark Sidebar, Light Content)
# ============================================================================
LIGHT_PALETTE = ColorPalette(
    # === BASE COLORS ===
    background="#ffffff",        # Pure white background
    surface="#ffffff",           # Pure white surface
    surface_light="#f8f9fa",     # Very light grey for hover/cards
    
    # === BLUE COLORS ===
    primary="#1890ff",           # Primary blue
    primary_light="#40a9ff",     # Light blue
    primary_dark="#0050b3",      # Darker primary
    primary_very_light="#e6f7ff",  # Very light blue for active items
    
    # === TEXT COLORS ===
    text_primary="#0050b3",      # Dark blue for main text
    text_secondary="#1890ff",    # Medium blue for secondary text
    text_tertiary="#bfbfbf",     # Very light grey
    
    # === BORDERS & DIVIDERS ===
    border="#d9d9d9",            # Grey border
    border_light="#f0f0f0",      # Very light grey border
    divider="#e8e8e8",           # Divider color
    
    # === SEMANTIC COLORS ===
    success="#52c41a",           # Green
    success_light="#f6ffed",     # Light green
    warning="#faad14",           # Orange
    warning_light="#fff7e6",     # Light orange
    danger="#ff4d4f",            # Red
    danger_light="#fff1f0",      # Light red
    info="#1890ff",              # Blue
    info_light="#e6f7ff",        # Light blue
    
    # === ROLE-BASED COLORS ===
    role_admin="#722ed1",        # Purple
    role_doctor="#1890ff",       # Blue
    role_secretary="#13c2c2",    # Teal
    role_assistant="#52c41a",    # Green
    role_patient="#fa8c16",      # Orange
)

# ============================================================================
# BLUE & WHITE THEME - Enhanced professional with stronger blue
# ============================================================================
BLUE_WHITE_PALETTE = ColorPalette(
    # === BASE COLORS ===
    background="#ffffff",          # Pure white
    surface="#f0f5fb",             # Blue-tinted white
    surface_light="#e6f2ff",       # Light blue
    
    # === BLUE COLORS ===
    primary="#0050b3",             # Darker primary blue
    primary_light="#1890ff",       # Medium blue
    primary_dark="#003a8c",        # Even darker for active
    primary_very_light="#e6f7ff",  # Very light blue background
    
    # === TEXT COLORS (STRONG BLUE) ===
    text_primary="#0050b3",        # Dark blue text
    text_secondary="#1890ff",      # Medium blue text
    text_tertiary="#40a9ff",       # Light blue text
    
    # === BORDERS & DIVIDERS ===
    border="#91caff",              # Blue border
    border_light="#bae0ff",        # Light blue border
    divider="#f0f5fb",             # Blue-tinted divider
    
    # === SEMANTIC COLORS ===
    success="#52c41a",             # Green (success)
    success_light="#f6ffed",       # Light green background
    warning="#faad14",             # Orange (warning)
    warning_light="#fff7e6",       # Light orange background
    danger="#f5222d",              # Red (error)
    danger_light="#fff1f0",        # Light red background
    info="#0050b3",                # Dark blue (info)
    info_light="#e6f7ff",          # Light blue background
    
    # === ROLE-BASED COLORS (BLUE TONES) ===
    role_admin="#0050b3",          # Dark blue (admin)
    role_doctor="#1890ff",         # Medium blue (doctor)
    role_secretary="#13c2c2",      # Teal (secretary)
    role_assistant="#52c41a",      # Green (assistant)
    role_patient="#fa8c16",        # Orange (patient)
)

# ============================================================================
# THEME REGISTRY
# ============================================================================
THEME_REGISTRY: Dict[ThemeType, ColorPalette] = {
    ThemeType.LIGHT: LIGHT_PALETTE,
    ThemeType.BLUE_WHITE: BLUE_WHITE_PALETTE,
}
