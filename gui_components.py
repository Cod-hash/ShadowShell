import customtkinter as ctk
from config import *
from utils import LocalImageLoader
from gamification import game_engine

# --- CARD DE PASTA (SITE / ALVO) ---
class SiteFolderCard(ctk.CTkFrame):
    def __init__(self, master, site_data, open_folder_callback):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color="#333")
        self.pack(pady=10, padx=20, fill="x")
        self.callback = open_folder_callback
        self.data = site_data
        
        user_xp = game_engine.data['xp']
        is_locked = user_xp < site_data['min_xp']
        
        self.grid_columnconfigure(1, weight=1)
        
        icon = "🔒" if is_locked else "🌐"
        ctk.CTkLabel(self, text=icon, font=("Arial", 35)).grid(row=0, column=0, padx=25, pady=25)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=10, pady=15)
        
        title_color = "#555" if is_locked else COLOR_ACCENT_BLUE
        ctk.CTkLabel(content, text=site_data['name'].upper(), font=("Arial", 18, "bold"), text_color=title_color).pack(anchor="w")
        
        req_color = COLOR_ACCENT_RED if is_locked else "#777"
        ctk.CTkLabel(content, text=f"REQUISITO: {site_data['min_xp']} XP", font=("Arial", 10, "bold"), text_color=req_color).pack(anchor="w", pady=(2, 5))
        
        ctk.CTkLabel(content, text=site_data['desc'], font=("Roboto", 12), text_color="#aaa", 
                     wraplength=450, justify="left").pack(anchor="w")
        
        btn_state = "disabled" if is_locked else "normal"
        btn_fg = "#222" if is_locked else COLOR_ACCENT_BLUE
        btn_text = "BLOQUEADO" if is_locked else "EXPLORAR ALVO"
        
        self.btn = ctk.CTkButton(self, text=btn_text, state=btn_state, fg_color=btn_fg, 
                                 hover_color="#1a5fb4", command=self.open_folder, 
                                 height=40, width=160, font=("Arial", 12, "bold"))
        self.btn.grid(row=0, column=2, padx=20)

    def open_folder(self):
        self.callback(self.data)


# --- CARD DE MISSÃO (FERRAMENTA ESPECÍFICA) ---
class ResultCard(ctk.CTkFrame):
    def __init__(self, master, tool_id, tool_data, target_ip, start_mission_callback):
        super().__init__(master, fg_color="#161616", corner_radius=12, border_width=1, border_color="#2a2a2a")
        self.pack(pady=8, padx=20, fill="x")
        self.start = start_mission_callback
        
        self.mission_payload = {
            "name": tool_data['name'],
            "steps": tool_data['steps'],
            "tool": tool_data['tool'],
            "ip": target_ip,
            "xp_reward": tool_data.get('xp_reward', 100) # Garante que o XP vá junto
        }
        
        self.grid_columnconfigure(1, weight=1)
        
        img = LocalImageLoader.get_image(tool_data['img'])
        if img: 
            ctk.CTkLabel(self, text="", image=img).grid(row=0, column=0, padx=15, pady=10)
        else:
            ctk.CTkLabel(self, text="🛠️", font=("Arial", 25)).grid(row=0, column=0, padx=15, pady=10)

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=0, column=1, sticky="nsew", padx=10, pady=12)
        
        ctk.CTkLabel(info, text=tool_data['name'], font=("Roboto", 15, "bold"), text_color="white").pack(anchor="w")
        
        ctk.CTkLabel(info, text=tool_data['desc'], font=("Roboto", 11), text_color="#888", 
                     wraplength=580, justify="left").pack(anchor="w", pady=(2, 0))
        
        ctk.CTkLabel(self, text=f"+{tool_data['xp_reward']} XP", font=("Arial", 13, "bold"), 
                     text_color=COLOR_ACCENT_GOLD).grid(row=0, column=2, padx=15)
        
        ctk.CTkButton(self, text="EXECUTAR", width=100, height=35, corner_radius=8, 
                      fg_color=COLOR_ACCENT_GREEN, text_color="#000", font=("Arial", 11, "bold"),
                      hover_color="#00c853", command=self.run).grid(row=0, column=3, padx=15)

    def run(self):
        self.start(self.mission_payload)

# --- NOVO: POPUP DE CONQUISTA ---
class AchievementToast(ctk.CTkFrame):
    def __init__(self, master, achievement_name):
        super().__init__(master, fg_color="#2b2b2b", corner_radius=20, border_width=2, border_color=COLOR_ACCENT_GOLD)
        

        
        self.icon = ctk.CTkLabel(self, text="🏆", font=("Arial", 30))
        self.icon.pack(side="left", padx=(20, 10), pady=15)
        
        self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.text_frame.pack(side="left", padx=(0, 20), pady=10)
        
        ctk.CTkLabel(self.text_frame, text="CONQUISTA DESBLOQUEADA!", 
                     font=("Arial", 10, "bold"), text_color=COLOR_ACCENT_GOLD).pack(anchor="w")
        
        ctk.CTkLabel(self.text_frame, text=achievement_name, 
                     font=("Arial", 14, "bold"), text_color="white").pack(anchor="w")
        
        # Posicionamento (Place no canto inferior direito)
        # Ajuste o rely/relx conforme sua resolução se necessário
        self.place(relx=0.98, rely=0.95, anchor="se")
        
        # Auto-destruição após 4 segundos
        self.after(4000, self.destroy_toast)

    def destroy_toast(self):
        self.destroy()