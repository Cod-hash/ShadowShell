"""
Configuration module for ShadowShell Academy.

This module sets up the appearance and color scheme for the CustomTkinter GUI,
defining constants for colors used throughout the application.
"""

import customtkinter as ctk

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Color constants for consistent theming
COLOR_BG = "#050505"
COLOR_CARD = "#141414"
COLOR_ACCENT_GREEN = "#00e676"  # Primary color focusing on success/learning
COLOR_ACCENT_RED = "#ff2a2a"    # Used for errors only
COLOR_ACCENT_BLUE = "#2979ff"
COLOR_ACCENT_GOLD = "#ffd700"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_DIM = "#a0a0a0"
