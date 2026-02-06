import customtkinter as ctk
import os
import time
from PIL import Image
from config import *
from data import MISSION_MAP, TOOLS_DB
from gamification import game_engine
from gui_components import SiteFolderCard, ResultCard, AchievementToast
from windows import FlashcardFrame, QuizFrame, MissionFlowFrame, AchievementsFrame, SandboxFrame
from utils import roll_number, glitch_effect

class DragonSplash(ctk.CTkToplevel):
    def __init__(self, parent, on_splash_complete):
        self.after_ids = []
        super().__init__(parent)
        self.on_splash_complete = on_splash_complete
        self.title("")
        self.state("zoomed")
        self.configure(fg_color="black")
        self.attributes("-alpha", 0)
        self.alpha = 0
        self.destroyed = False

        # Carregar imagem do dragão
        try:
            img = Image.open("img/kali.png")
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.ctk_image = ctk.CTkImage(img, size=(screen_width, screen_height))
            self.lbl_dragon = ctk.CTkLabel(self, image=self.ctk_image, text="")
            self.lbl_dragon.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.lbl_dragon = ctk.CTkLabel(self, text="🐉", font=("Arial", 200))
            self.lbl_dragon.place(relx=0.5, rely=0.5, anchor="center")

        # Override callit to prevent errors on destroyed widgets
        def _safe_callit(func, *args):
            try:
                func(*args)
            except:
                pass
        self.lbl_dragon.callit = _safe_callit

        # Barra de progresso fina
        self.progress = ctk.CTkProgressBar(self, width=400, height=10, progress_color=COLOR_ACCENT_BLUE)
        self.progress.place(relx=0.5, rely=0.85, anchor="center")
        self.progress.set(0)

        self.fade_in()

    def destroy(self):
        self.destroyed = True
        for id in self.after_ids:
            try:
                self.after_cancel(id)
            except:
                pass
        self.after_ids = []
        super().destroy()

    def focus_set(self):
        try:
            if not self.destroyed:
                super().focus_set()
        except:
            pass

    def callit(self, func, *args):
        try:
            super().callit(func, *args)
        except:
            pass

    def fade_in(self):
        if self.destroyed:
            return
        self.alpha += 0.033  # 30 passos para 1.5s (30*50=1500ms)
        if self.alpha > 1.0:
            self.alpha = 1.0
        self.attributes("-alpha", self.alpha)
        self.progress.set(self.alpha)  # Progresso segue o fade
        if self.alpha < 1.0:
            self.after(50, self.fade_in)
        else:
            self.after(1000, self.finish_splash)  # Espera 1s, total 2.5s

    def finish_splash(self):
        if not self.destroyed:
            self.on_splash_complete()
            self.after(10, self.destroy)

    def after(self, ms, func=None, *args):
        id = super().after(ms, func, *args)
        self.after_ids.append(id)
        return id

class BootSequence(ctk.CTkToplevel):
    def __init__(self, parent, on_boot_complete):
        self.after_ids = []
        super().__init__(parent)
        self.on_boot_complete = on_boot_complete
        self.title("")
        # Tenta maximizar (Cross-Platform)
        try:
            self.state("zoomed")  #windows
        except:
            try:
                self.attributes("-zoomed", True)   #Linux
            except:
                self.state("normal")  # Fallback se tudo der errado
        self.configure(fg_color="black")
        self.destroyed = False

        self.lbl_boot = ctk.CTkLabel(self, text="", font=("Consolas", 14), text_color="#00ff00", justify="left")
        self.lbl_boot.pack(expand=True, fill="both", padx=50, pady=50)

        # Override callit to prevent errors on destroyed widgets
        def _safe_callit(func, *args):
            if not self.destroyed:
                try:
                    func(*args)
                except:
                    pass
        self.lbl_boot.callit = _safe_callit

        self.logs = [
            "[ OK ] Mounted /dev/sda1 (ShadowShell FS)",
            "[ OK ] Started Network Time Synchronization.",
            "[ OK ] Reached target System Initialization.",
            "[ OK ] Started SSH Key Generation.",
            "[....] Loading ShadowShell Academy Modules...",
            "[ OK ] Module 'Hydra' loaded.",
            "[ OK ] Module 'Nmap' loaded.",
            "[ OK ] Starting Graphical Interface...",
        ]

        self.current_log = 0
        self.lbl_boot.configure(text="")
        self.add_log()

    def destroy(self):
        self.destroyed = True
        for id in self.after_ids:
            try:
                self.after_cancel(id)
            except:
                pass
        self.after_ids = []
        super().destroy()

    def focus_set(self):
        try:
            if not self.destroyed:
                super().focus_set()
        except:
            pass

    def add_log(self):
        if self.destroyed:
            return
        if self.current_log < len(self.logs):
            current_text = self.lbl_boot.cget("text")
            self.lbl_boot.configure(text=current_text + self.logs[self.current_log] + "\n")
            self.current_log += 1
            self.after(500, self.add_log)  # 500ms por linha
        else:
            self.after(3500 - (len(self.logs) * 500), self.finish_boot)  # total 3.5s

    def finish_boot(self):
        if not self.destroyed:
            self.on_boot_complete()
            self.after(0, self.destroy)

    def after(self, ms, func=None, *args):
        id = super().after(ms, func, *args)
        self.after_ids.append(id)
        return id

class WelcomeScreen(ctk.CTkToplevel):
    def __init__(self, parent, on_login):
        self.after_ids = []
        super().__init__(parent)
        self.on_login = on_login
        self.title("ShadowShell - Offensive Security Simulator")

        # Centraliza e ajusta tamanho
        w, h = 500, 400
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLOR_BG)

        container = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=20, border_width=2, border_color=COLOR_ACCENT_BLUE)
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text="🎭", font=("Arial", 60)).pack(pady=(30, 10))
        ctk.CTkLabel(container, text="ShadowShell ACADEMY", font=("Arial", 24, "bold"), text_color=COLOR_ACCENT_BLUE).pack(pady=5)
        ctk.CTkLabel(container, text="Simulador de Pentest Educacional", font=("Arial", 12), text_color="#888").pack(pady=(0, 20))

        ctk.CTkLabel(container, text="ESCOLHA SEU CODINOME:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.entry = ctk.CTkEntry(container, placeholder_text="Ex: Neo, Trinity, Morpheus...", width=280, height=40,
                                   justify="center", font=("Arial", 14))
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self.login())

        # Override callit to prevent errors on destroyed widgets
        def _safe_callit(func, *args):
            if not self.destroyed:
                try:
                    func(*args)
                except:
                    pass
        self.entry.callit = _safe_callit

        ctk.CTkButton(container, text="🚀 INICIAR JORNADA", command=self.login, width=280, height=45,
                      fg_color=COLOR_ACCENT_GREEN, text_color="black", font=("Arial", 14, "bold"),
                      hover_color="#00b35c").pack(pady=20)

        ctk.CTkLabel(container, text="Sua evolução será salva automaticamente",
                     font=("Arial", 10), text_color="#666").pack(pady=(0, 20))

    def login(self):
        name = self.entry.get().strip()
        if name:
            game_engine.set_player_name(name)
            self.on_login(name)
            self.destroy()

    def after(self, ms, func=None, *args):
        id = super().after(ms, func, *args)
        self.after_ids.append(id)
        return id

    def destroy(self):
        for id in self.after_ids:
            try:
                self.after_cancel(id)
            except:
                pass
        self.after_ids = []
        super().destroy()

class ScannerDashboard(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("ShadowShell - Offensive Security Simulator")
        
        # --- CORREÇÃO DE TELA ---
        # 1. Obtém o tamanho da tela do usuário
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 2. Define o tamanho ideal (1200x800) OU 90% da tela se for menor
        target_w = min(1200, int(screen_width * 0.9))
        target_h = min(800, int(screen_height * 0.9))
        
        # 3. Centraliza a janela
        pos_x = int((screen_width / 2) - (target_w / 2))
        pos_y = int((screen_height / 2) - (target_h / 2))
        
        self.geometry(f"{target_w}x{target_h}+{pos_x}+{pos_y}")
        
        # 4. IMPORTANTE: Permite redimensionar manualmente
        self.resizable(True, True) 
        self.minsize(800, 600) # Tamanho mínimo para não quebrar o layout
        
        # Configuração do Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Observer de Conquistas
        game_engine.add_observer(self.handle_gamification_event)

        # Sidebar (Barra Lateral)
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False) # Garante que a largura da sidebar não mude
        
        # Perfil
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color=COLOR_CARD, corner_radius=15)
        profile_frame.pack(pady=20, padx=15, fill="x")
        
        self.lbl_avatar = ctk.CTkLabel(profile_frame, text="👶", font=("Arial", 50))
        self.lbl_avatar.pack(pady=(15, 5))
        
        self.lbl_name = ctk.CTkLabel(profile_frame, text="Recruta", font=("Arial", 16, "bold"), text_color=COLOR_ACCENT_GREEN)
        self.lbl_name.pack(pady=5)
        
        self.lbl_rank = ctk.CTkLabel(profile_frame, text="Script Kiddie", font=("Arial", 12), text_color="#888")
        self.lbl_rank.pack()
        
        # XP Bar
        xp_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        xp_frame.pack(pady=10, padx=15, fill="x")
        
        self.lbl_xp = ctk.CTkLabel(xp_frame, text="Lvl 1 • 0 XP", font=("Arial", 11, "bold"), text_color=COLOR_ACCENT_BLUE)
        self.lbl_xp.pack()

        self.progress_xp = ctk.CTkProgressBar(xp_frame, width=200, height=8, progress_color=COLOR_ACCENT_BLUE)
        self.progress_xp.pack(pady=5)
        self.progress_xp.set(0)

        self.lbl_next = ctk.CTkLabel(xp_frame, text="Próximo: Neophyte", font=("Arial", 9), text_color="#666")
        self.lbl_next.pack()

        self.previous_xp = 0
        
        # Stats
        stats_frame = ctk.CTkFrame(profile_frame, fg_color="#111", corner_radius=10)
        stats_frame.pack(pady=10, padx=15, fill="x")
        
        self.lbl_stats = ctk.CTkLabel(stats_frame, text="📊 Estatísticas\n━━━━━━━━━━━━\nMissões: 0\nPerfeitas: 0\nComandos: 0", 
                                      font=("Consolas", 10), text_color="#aaa", justify="left")
        self.lbl_stats.pack(pady=10)
        
        # Navegação
        ctk.CTkLabel(self.sidebar, text="━━━━━━━━━━━━━━━━━━━━", text_color="#222").pack(pady=10)
        self.nav_btn("🌍 MAPA MUNDI", "HUB")
        self.nav_btn("📇 FLASHCARDS", "FLASH")
        self.nav_btn("🧠 HACK QUIZ", "QUIZ")
        self.nav_btn("🏆 CONQUISTAS", "ACHIEV")
        self.nav_btn("💻 SANDBOX", "SANDBOX")
        # Área de Conteúdo Principal
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.current_frame = None
        self.show_view("HUB")
        self.update_sidebar_data()

    def handle_gamification_event(self, event_type, data):
        self.update_sidebar_data()
        if event_type == "achievement":
            AchievementToast(self, data)

    def nav_btn(self, text, view_name):
        ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", hover_color="#222", 
                      anchor="w", height=50, font=("Arial", 13, "bold"),
                      command=lambda: self.show_view(view_name)).pack(fill="x", padx=10, pady=2)

    def set_user_name(self, name):
        self.lbl_name.configure(text=f"{name}")

    def update_sidebar_data(self):
        try:
            icon = game_engine.get_rank_icon()
            rank = game_engine.get_rank_title()
            color = game_engine.get_rank_color()
            
            self.lbl_avatar.configure(text=icon)
            self.lbl_rank.configure(text=rank, text_color=color)
            
            level = game_engine.data['level']
            xp = game_engine.data['xp']

            xp_current_level = (level - 1) * 200
            progress = (xp - xp_current_level) / 200
            progress = max(0, min(1, progress))

            if xp != self.previous_xp:
                roll_number(self.lbl_xp, self.previous_xp, xp, prefix=f"Lvl {level} • ", suffix=" XP")
                self.previous_xp = xp
            self.progress_xp.set(progress)
            
            next_rank = game_engine.get_next_rank()
            if next_rank:
                self.lbl_next.configure(text=f"Próximo: {next_rank['icon']} {next_rank['name']} ({next_rank['xp_needed']} XP)")
            else:
                self.lbl_next.configure(text="🏆 Rank Máximo Alcançado!")
            
            stats = game_engine.get_stats()
            stats_text = f"📊 Estatísticas\n━━━━━━━━━━━━\nMissões: {stats['missions']}\nPerfeitas: {stats['perfect']}\nComandos: {stats['commands']}"
            self.lbl_stats.configure(text=stats_text)
            
            if hasattr(self.current_frame, "refresh_map") and self.current_frame.winfo_exists():
                self.current_frame.refresh_map()
        except Exception as e:
            print(f"Erro ao atualizar sidebar: {e}")

    def show_view(self, view_name):
        for widget in self.content_area.winfo_children(): widget.destroy()
            
        if view_name == "HUB":
            self.current_frame = HubFrame(self.content_area, self.open_site_folder)
            self.current_frame.pack(fill="both", expand=True)
        elif view_name == "FLASH":
            self.current_frame = FlashcardFrame(self.content_area)
            self.current_frame.pack(fill="both", expand=True)
        elif view_name == "QUIZ":
            self.current_frame = QuizFrame(self.content_area)
            self.current_frame.pack(fill="both", expand=True)
        elif view_name == "ACHIEV":
            self.current_frame = AchievementsFrame(self.content_area)
            self.current_frame.pack(fill="both", expand=True)
        elif view_name == "SANDBOX": # <--- NOVA CONDIÇÃO
            self.current_frame = SandboxFrame(self.content_area)
            self.current_frame.pack(fill="both", expand=True)
    def open_site_folder(self, site_data):
        for widget in self.content_area.winfo_children(): widget.destroy()
        self.current_frame = SiteContentFrame(self.content_area, site_data, self.start_mission, lambda: self.show_view("HUB"))
        self.current_frame.pack(fill="both", expand=True)

    def start_mission(self, mission_data):
        for widget in self.content_area.winfo_children(): widget.destroy()
        current_site_data = next((s for s in MISSION_MAP if s['ip'] == mission_data['ip']), None)
        return_cb = lambda: self.show_view("HUB")
        if current_site_data:
            return_cb = lambda: self.open_site_folder(current_site_data)

        self.current_frame = MissionFlowFrame(self.content_area, mission_data, return_cb)
        self.current_frame.pack(fill="both", expand=True)

class HubFrame(ctk.CTkFrame):
    def __init__(self, parent, open_site_cb):
        super().__init__(parent, fg_color="transparent")
        self.open_cb = open_site_cb
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=40)
        
        ctk.CTkLabel(header, text="🌍 MAPA DE ALVOS GLOBAIS", font=("Roboto", 26, "bold"), 
                     text_color=COLOR_ACCENT_BLUE).pack(side="left")
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_map()
        
    def refresh_map(self):
        for w in self.scroll.winfo_children(): w.destroy()
        for site in MISSION_MAP:
            SiteFolderCard(self.scroll, site, self.open_cb)

class SiteContentFrame(ctk.CTkFrame):
    def __init__(self, parent, site_data, start_mission_cb, back_cb):
        super().__init__(parent, fg_color="transparent")
        header = ctk.CTkFrame(self, height=80, fg_color="#111")
        header.pack(fill="x", side="top")
        ctk.CTkButton(header, text="⬅ VOLTAR AO MAPA", width=150, fg_color="#333", command=back_cb).pack(side="left", padx=20)
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left", padx=20)
        ctk.CTkLabel(info, text=f"ALVO: {site_data['name']}", font=("Arial", 20, "bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w")
        ctk.CTkLabel(info, text=f"IP: {site_data['ip']}", font=("Consolas", 12), text_color="#777").pack(anchor="w")
        ctk.CTkLabel(self, text="VETORES DE ATAQUE DISPONÍVEIS", font=("Arial", 14, "bold"), text_color="gray").pack(pady=20, anchor="w", padx=40)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        for tool_id in site_data['tools']:
            if tool_id in TOOLS_DB:
                tool_data = TOOLS_DB[tool_id]
                ResultCard(self.scroll, tool_id, tool_data, site_data['ip'], start_mission_cb)

class RootApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        DragonSplash(self, self.show_boot_sequence)

    def show_boot_sequence(self):
        BootSequence(self, self.show_welcome)

    def show_welcome(self):
        WelcomeScreen(self, self.start)

    def start(self, name):
        dash = ScannerDashboard(self)
        dash.set_user_name(name)
        dash.protocol("WM_DELETE_WINDOW", self.quit)

if __name__ == "__main__":
    app = RootApp()
    app.mainloop()
