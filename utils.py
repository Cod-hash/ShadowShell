"""
Utility functions for ShadowShell Academy.

This module provides helper classes and functions for image loading,
animation effects, and UI enhancements in the cybersecurity training platform.
"""

import os
import customtkinter as ctk
from PIL import Image
import requests
import random
import time


class LocalImageLoader:
    _cache = {}
    @classmethod
    def get_image(cls, key_name):
        if key_name in cls._cache: return cls._cache[key_name]
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))

            # Tenta encontrar .png primeiro, depois .jpg
            image_path_png = os.path.join(base_path, "img", f"{key_name}.png")
            image_path_jpg = os.path.join(base_path, "img", f"{key_name}.jpg")

            final_path = None
            if os.path.exists(image_path_png):
                final_path = image_path_png
            elif os.path.exists(image_path_jpg):
                final_path = image_path_jpg

            if not final_path: return None

            pil_image = Image.open(final_path)
            ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(50, 50))
            cls._cache[key_name] = ctk_img
            return ctk_img
        except: return None

# --- ANIMATION UTILITIES ---

def decodify_text(widget, final_text, duration=1.0, chars="#?&#01"):
    """Animate text revealing like Hollywood hacker style"""
    steps = int(duration * 10)  # 10 fps
    length = len(final_text)
    current = [" "] * length

    def animate(step=0):
        if step >= steps:
            widget.configure(text=final_text)
            return

        for i in range(length):
            if random.random() < 0.3:  # Chance to lock in correct char
                current[i] = final_text[i]
            else:
                current[i] = random.choice(chars)

        widget.configure(text="".join(current))
        widget.after(100, animate, step + 1)

    animate()

def roll_number(widget, start, end, duration=1.0, prefix="", suffix=""):
    """Animate number rolling up"""
    if start >= end:
        widget.configure(text=f"{prefix}{end}{suffix}")
        return

    steps = int(duration * 20)  # 20 fps
    diff = end - start
    step_size = diff / steps

    def animate(current=start, step=0):
        if step >= steps:
            widget.configure(text=f"{prefix}{end}{suffix}")
            return

        current += step_size
        display = int(current)
        widget.configure(text=f"{prefix}{display}{suffix}")
        widget.after(50, animate, current, step + 1)

    animate()

def pulse_color(widget, color1, color2, interval=500):
    """Pulse between two colors"""
    def pulse():
        current = widget.cget("text_color")
        next_color = color2 if current == color1 else color1
        widget.configure(text_color=next_color)
        widget.after(interval, pulse)
    pulse()

def glitch_effect(widget, duration=100):
    """Flash widget in red/invert colors"""
    original_fg = widget.cget("fg_color")
    original_text = widget.cget("text_color") if hasattr(widget, 'cget') and 'text_color' in widget.configure() else None

    widget.configure(fg_color="#ff0000")
    if original_text:
        widget.configure(text_color="#ffffff")

    def restore():
        widget.configure(fg_color=original_fg)
        if original_text:
            widget.configure(text_color=original_text)

    widget.after(duration, restore)
