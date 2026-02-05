"""
Gamification engine for ShadowShell Academy.

This module implements the XP, leveling, and achievement system for the
cybersecurity learning platform, providing motivation and progress tracking.
"""

import os
import json
import time
import shutil


class GamificationEngine:
    FILE_NAME = "student_save.json"
    
    HACKER_AVATARS = {
        1: {"icon": "👶", "name": "Script Kiddie", "color": "#888888"},
        2: {"icon": "🎓", "name": "Neophyte", "color": "#4a9eff"},
        5: {"icon": "⚔️", "name": "Apprentice", "color": "#00e676"},
        10: {"icon": "🎭", "name": "Anonymous", "color": "#ffd700"},
        15: {"icon": "💀", "name": "Black Hat", "color": "#ff2a2a"},
        20: {"icon": "👑", "name": "Elite Hacker", "color": "#9c27b0"},
        30: {"icon": "🔱", "name": "Cyber God", "color": "#00ffff"}
    }
    
    XP_PER_LEVEL = 200

    def __init__(self):
        self.data = self.load_data()
        self._observers = []

    def load_data(self):
        default_data = {
            "player_name": "NEO", "xp": 0, "level": 1, 
            "completed_missions": [], "achievements_unlocked": [],
            "total_missions": 0, "perfect_runs": 0, "total_commands": 0, "total_errors": 0,
            "settings": {
                "theme": "Dark",      # Dark, Light, System
                "animations": True,   # Ativar/Desativar efeito typewriter
                "sound": False
            }, 
            "statistics": {"tools_used": {}}
        }
        if not os.path.exists(self.FILE_NAME): return default_data
        try:
            with open(self.FILE_NAME, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in default_data.items():
                    if k not in data: data[k] = v
                # Garante que settings existam
                if "settings" not in data: data["settings"] = default_data["settings"]
                return data
        except: return default_data

    def save_data(self):
        try:
            with open(self.FILE_NAME, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except: pass

    # --- SETTINGS MANAGEMENT ---
    def get_setting(self, key):
        return self.data["settings"].get(key, None)

    def set_setting(self, key, value):
        self.data["settings"][key] = value
        self.save_data()
        # Notifica observadores que as configs mudaram (para atualizar tema em tempo real)
        self._notify_observers("settings_changed", key)

    def add_xp(self, amount):
        self.data["xp"] = max(0, self.data["xp"] + amount)
        new_level = (self.data["xp"] // self.XP_PER_LEVEL) + 1
        if new_level > self.data["level"]:
            self.data["level"] = new_level
            self._notify_observers("level_up", new_level)
        self.save_data()
        self.check_achievements()

    def complete_mission(self, mission_data, perfect=False):
        self.data["total_missions"] += 1
        if perfect: self.data["perfect_runs"] += 1
        
        record = {
            "name": mission_data.get('name', 'Unknown'),
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "perfect": perfect
        }
        self.data["completed_missions"].append(record)
        self.save_data()
        self.check_achievements()

    def check_achievements(self):
        from data import ACHIEVEMENTS_DB
        current_stats = {
            "missions": self.data["total_missions"],
            "level": self.data["level"],
            "perfect": self.data["perfect_runs"],
            "commands": self.data["total_commands"],
            "errors": self.data.get("total_errors", 0),
            "xp": self.data["xp"]
        }
        
        for ach_id, ach_info in ACHIEVEMENTS_DB.items():
            if ach_id not in self.data["achievements_unlocked"]:
                try:
                    if ach_info["requirement"](current_stats):
                        self.data["achievements_unlocked"].append(ach_id)
                        self._notify_observers("achievement", ach_info["name"])
                except Exception as e:
                    print(f"Erro achievement {ach_id}: {e}")
        self.save_data()

    def add_observer(self, callback): self._observers.append(callback)
    def _notify_observers(self, event, data):
        for cb in self._observers: 
            try: cb(event, data)
            except: pass

    def get_stats(self):
        return {
            "missions": self.data["total_missions"],
            "perfect": self.data["perfect_runs"],
            "commands": self.data["total_commands"],
            "modules": 0
        }

    def get_rank_title(self):
        lvl = self.data["level"]
        for t in sorted(self.HACKER_AVATARS.keys(), reverse=True):
            if lvl >= t: return self.HACKER_AVATARS[t]["name"]
        return "Script Kiddie"

    def get_rank_icon(self):
        lvl = self.data["level"]
        for t in sorted(self.HACKER_AVATARS.keys(), reverse=True):
            if lvl >= t: return self.HACKER_AVATARS[t]["icon"]
        return "👶"

    def get_rank_color(self):
        lvl = self.data["level"]
        for t in sorted(self.HACKER_AVATARS.keys(), reverse=True):
            if lvl >= t: return self.HACKER_AVATARS[t]["color"]
        return "#888"

    def get_next_rank(self):
        lvl = self.data["level"]
        for t in sorted(self.HACKER_AVATARS.keys()):
            if t > lvl:
                return {"name": self.HACKER_AVATARS[t]["name"], "icon": self.HACKER_AVATARS[t]["icon"], "xp_needed": (t-1)*200 - self.data["xp"]}
        return None
        
    def add_command(self, count=1):
        self.data["total_commands"] += count
        self.save_data()
        self.check_achievements()

    def add_error(self, count=1):
        self.data["total_errors"] = self.data.get("total_errors", 0) + count
        self.save_data()
        self.check_achievements()

    def get_player_name(self): return self.data.get("player_name", "NEO")
    def set_player_name(self, name): self.data["player_name"] = name; self.save_data()
    
    def reset_progress(self):
        """Reseta o progresso mantendo o nome"""
        name = self.data["player_name"]
        settings = self.data["settings"]
        if os.path.exists(self.FILE_NAME):
            os.remove(self.FILE_NAME)
        self.data = self.load_data()
        self.data["player_name"] = name
        self.data["settings"] = settings
        self.save_data()
        return True

game_engine = GamificationEngine()