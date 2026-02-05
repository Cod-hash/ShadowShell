import customtkinter as ctk
import random
import time
import threading
import os
from config import *
from data import TOOLS_DB, ACHIEVEMENTS_DB
from gamification import game_engine
from utils import pulse_color, glitch_effect, decodify_text

# ==========================================
# 1. RELATÓRIOS E CONQUISTAS
# ==========================================

class MissionReport(ctk.CTkFrame): 
    def __init__(self, parent, history_log, final_message, is_success, close_callback, mission_name="Unknown"):
        super().__init__(parent, fg_color="transparent")
        
        # Salva o resultado
        game_engine.complete_mission({"name": mission_name}, perfect=is_success and all(h['status'] == 'SUCCESS' for h in history_log))
        
        bg_color = "#051a05" if is_success else "#1a0505"
        accent_color = COLOR_ACCENT_GREEN if is_success else "#ff5555"
        
        self.bg = ctk.CTkFrame(self, fg_color=bg_color)
        self.bg.pack(fill="both", expand=True)
        
        title_text = "MISSÃO CUMPRIDA" if is_success else "FALHA NA MISSÃO"
        ctk.CTkLabel(self.bg, text=title_text, font=("Arial", 28, "bold"), text_color=accent_color).pack(pady=(30, 5))
        ctk.CTkLabel(self.bg, text=final_message, font=("Roboto", 14), text_color="#ccc", wraplength=700).pack(pady=10)
        
        ctk.CTkLabel(self.bg, text="📝 DEBRIEFING TÁTICO", font=("Arial", 16, "bold"), text_color="white").pack(pady=(20, 5))
        
        scroll = ctk.CTkScrollableFrame(self.bg, fg_color="transparent", height=400)
        scroll.pack(fill="both", expand=True, padx=50, pady=10)
        
        if not history_log:
            ctk.CTkLabel(scroll, text="Nenhuma ação registrada.", text_color="gray").pack()
        
        for m in history_log:
            self.create_log_entry(scroll, m)
            
        ctk.CTkButton(self.bg, text="VOLTAR AO QG", command=close_callback, 
                      fg_color=accent_color, text_color="black" if is_success else "white", 
                      height=50, width=250, font=("Arial", 14, "bold"), hover_color="#fff").pack(pady=30)

    def create_log_entry(self, parent, action):
        colors = { "SUCCESS": ("#1b5e20", "#4caf50"), "FAIL": ("#b71c1c", "#ff5252"), "FATAL": ("#310000", "#ff0000"), "NEUTRAL": ("#222", "#777") }
        bg, fg = colors.get(action['status'], colors["NEUTRAL"])
        card = ctk.CTkFrame(parent, fg_color=bg, border_width=1, border_color=fg, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(5, 0))
        icon = "✅" if action['status'] == 'SUCCESS' else "⚠️" if action['status'] == 'FAIL' else "☠️" if action['status'] == 'FATAL' else "ℹ️"
        
        ctk.CTkLabel(header, text=f"{icon} > {action['cmd']}", font=("Consolas", 14, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(header, text=action['status'], font=("Arial", 10, "bold"), text_color=fg).pack(side="right")
        ctk.CTkLabel(card, text=action['reason'], font=("Roboto", 12), text_color="#eee", wraplength=650, justify="left").pack(fill="x", padx=10, pady=5)

class AchievementsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ach_area = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        ach_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(ach_area, text="🏆 SUAS CONQUISTAS", font=("Arial", 20, "bold"), text_color=COLOR_ACCENT_BLUE).pack(pady=20)
        self.scroll_ach = ctk.CTkScrollableFrame(ach_area, fg_color="transparent")
        self.scroll_ach.pack(fill="both", expand=True, padx=10, pady=10)
        self.render_achievements()

        hist_area = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        hist_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(hist_area, text="📜 HISTÓRICO", font=("Arial", 18, "bold"), text_color=COLOR_ACCENT_GREEN).pack(pady=20)
        self.scroll_hist = ctk.CTkScrollableFrame(hist_area, fg_color="transparent")
        self.scroll_hist.pack(fill="both", expand=True, padx=10, pady=10)
        self.render_history()

    def render_achievements(self):
        unlocked = game_engine.data["achievements_unlocked"]
        for ach_id, info in ACHIEVEMENTS_DB.items():
            is_unlocked = ach_id in unlocked
            bg = "#1e1e1e" if is_unlocked else "#0a0a0a"
            text_alpha = "white" if is_unlocked else "#444"
            border = COLOR_ACCENT_GOLD if is_unlocked else "#222"
            
            card = ctk.CTkFrame(self.scroll_ach, fg_color=bg, border_width=1, border_color=border, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(card, text=info["icon"], font=("Arial", 30)).pack(side="left", padx=15)
            text_frame = ctk.CTkFrame(card, fg_color="transparent")
            text_frame.pack(side="left", fill="y", pady=10)
            ctk.CTkLabel(text_frame, text=info["name"], font=("Arial", 14, "bold"), text_color=text_alpha).pack(anchor="w")
            ctk.CTkLabel(text_frame, text=info["desc"], font=("Arial", 11), text_color="#777").pack(anchor="w")
            if is_unlocked: ctk.CTkLabel(card, text="✅", text_color=COLOR_ACCENT_GREEN).pack(side="right", padx=15)

    def render_history(self):
        missions = game_engine.data["completed_missions"][::-1]
        if not missions: ctk.CTkLabel(self.scroll_hist, text="Nenhuma missão registrada.", text_color="#555").pack(pady=20); return
        for m in missions:
            card = ctk.CTkFrame(self.scroll_hist, fg_color="#1a1a1a", corner_radius=5)
            card.pack(fill="x", pady=3)
            status_color = COLOR_ACCENT_GOLD if m.get("perfect") else "#aaa"
            ctk.CTkLabel(card, text=f"{m['name']}", font=("Consolas", 11, "bold"), text_color=status_color).pack(pady=5, padx=10, anchor="w")
            ctk.CTkLabel(card, text=m['date'], font=("Consolas", 9), text_color="#444").pack(padx=10, anchor="w")

# ==========================================
# 2. SETTINGS
# ==========================================

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        container = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=20)
        container.pack(expand=True, fill="both", padx=50, pady=50)
        ctk.CTkLabel(container, text="⚙️ CONFIGURAÇÕES DO SISTEMA", font=("Arial", 24, "bold"), text_color=COLOR_ACCENT_BLUE).pack(pady=30)
        
        # Tema
        ctk.CTkLabel(container, text="Tema da Interface:", font=("Arial", 14)).pack(pady=(20, 5))
        self.theme_var = ctk.StringVar(value=game_engine.get_setting("theme") or "Dark")
        combo_theme = ctk.CTkComboBox(container, values=["Dark", "Light", "System"], variable=self.theme_var, command=self.change_theme)
        combo_theme.pack(pady=5)
        
        # Animações
        self.anim_switch = ctk.CTkSwitch(container, text="Efeitos Visuais (Typewriter)", command=self.toggle_anim)
        if game_engine.get_setting("animations"): self.anim_switch.select()
        else: self.anim_switch.deselect()
        self.anim_switch.pack(pady=20)
        
        # Reset Data
        ctk.CTkLabel(container, text="Zona de Perigo", font=("Arial", 14, "bold"), text_color=COLOR_ACCENT_RED).pack(pady=(40, 10))
        ctk.CTkButton(container, text="⚠️ RESETAR TODO O PROGRESSO", fg_color="#b71c1c", hover_color="#ff0000", command=self.reset_progress).pack(pady=10)
        
    def change_theme(self, choice):
        game_engine.set_setting("theme", choice)
        ctk.set_appearance_mode(choice)
        
    def toggle_anim(self):
        game_engine.set_setting("animations", bool(self.anim_switch.get()))
        
    def reset_progress(self):
        if game_engine.reset_progress():
            ctk.CTkLabel(self, text="Reinicie o aplicativo para aplicar o reset.", text_color=COLOR_ACCENT_RED).pack()

# ==========================================
# 3. QUIZ E FLASHCARDS
# ==========================================

class FlashcardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.keys = list(TOOLS_DB.keys())
        self.current_key = None
        self.score = 0
        self.total_questions = 0
        self.streak = 0
        
        header = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=80)
        header.pack(fill="x", pady=(20, 10), padx=40)
        self.lbl_stats = ctk.CTkLabel(header, text="📊 Acertos: 0/0 | 🔥 Sequência: 0", font=("Arial", 16, "bold"), text_color=COLOR_ACCENT_BLUE)
        self.lbl_stats.pack(pady=20)
        
        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.place(relx=0.5, rely=0.5, anchor="center")
        self.card = ctk.CTkFrame(self.center, width=700, height=450, corner_radius=25, fg_color=COLOR_CARD, border_width=3, border_color=COLOR_ACCENT_BLUE)
        self.card.pack(pady=20)
        self.card.pack_propagate(False) 
        self.icon_label = ctk.CTkLabel(self.card, text="🔧", font=("Arial", 60))
        self.icon_label.pack(pady=(30, 10))
        self.lbl_text = ctk.CTkLabel(self.card, text="...", font=("Arial", 28, "bold"), text_color=COLOR_ACCENT_BLUE, wraplength=600)
        self.lbl_text.pack(pady=10)
        self.lbl_desc = ctk.CTkLabel(self.card, text="", font=("Arial", 14), text_color="#888", wraplength=650, justify="center")
        self.lbl_desc.pack(pady=10)
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(pady=20)
        self.btn = ctk.CTkButton(btn_frame, text="REVELAR RESPOSTA", command=self.flip, width=200, height=50, font=("Arial", 16, "bold"), fg_color=COLOR_ACCENT_BLUE)
        self.btn.pack()
        self.next_card()

    def next_card(self):
        self.current_key = random.choice(self.keys)
        data = TOOLS_DB[self.current_key]
        self.icon_label.configure(text="🔧")
        self.lbl_text.configure(text=f"PORTA {self.current_key}", text_color=COLOR_ACCENT_BLUE)
        self.lbl_desc.configure(text="Qual ferramenta é usada para explorar esta porta?", text_color="#888")
        self.btn.configure(text="REVELAR RESPOSTA", command=self.flip, fg_color=COLOR_ACCENT_BLUE)

    def flip(self):
        data = TOOLS_DB[self.current_key]
        self.lbl_text.configure(text=f"{data['name']}", text_color="white", font=("Arial", 24, "bold"))
        self.lbl_desc.configure(text=f"🛠️ {data['tool']}\n\n{data['desc'][:200]}...", text_color="#aaa", justify="center")
        self.btn.configure(text="ACERTEI! (+5 XP)", command=self.correct, fg_color=COLOR_ACCENT_GREEN)
        self.btn_wrong = ctk.CTkButton(self.card, text="ERREI (-2 XP)", command=self.wrong, width=150, height=40, fg_color="#ff5555", hover_color="#cc0000")
        self.btn_wrong.pack(pady=10)

    def correct(self):
        self.score += 1; self.streak += 1; self.total_questions += 1
        game_engine.add_xp(5)
        self.lbl_text.configure(text="✅ CORRETO!", text_color=COLOR_ACCENT_GREEN)
        self.after(1000, self.next_card)
        if hasattr(self, 'btn_wrong'): self.btn_wrong.destroy()
        self.update_stats()

    def wrong(self):
        self.streak = 0; self.total_questions += 1
        game_engine.add_xp(-2)
        self.lbl_text.configure(text="❌ INCORRETO", text_color="#ff5555")
        self.after(2000, self.next_card)
        if hasattr(self, 'btn_wrong'): self.btn_wrong.destroy()
        self.update_stats()

    def update_stats(self):
        acc = int((self.score / max(self.total_questions, 1)) * 100)
        self.lbl_stats.configure(text=f"📊 Acertos: {self.score}/{self.total_questions} ({acc}%) | 🔥 Sequência: {self.streak}")

class QuizFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        header = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=80)
        header.pack(fill="x", pady=(20, 10), padx=40)
        self.lbl_stats = ctk.CTkLabel(header, text="🎯 Questão 1/5 | Pontuação: 0", font=("Arial", 16, "bold"), text_color=COLOR_ACCENT_BLUE)
        self.lbl_stats.pack(pady=20)
        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.pack(expand=True, fill="both", padx=100, pady=50)
        self.question_card = ctk.CTkFrame(self.center, fg_color=COLOR_CARD, corner_radius=20, border_width=2, border_color=COLOR_ACCENT_BLUE)
        self.question_card.pack(pady=20, fill="x")
        self.lbl_q = ctk.CTkLabel(self.question_card, text="...", font=("Roboto", 20, "bold"), wraplength=600, text_color="white")
        self.lbl_q.pack(pady=30, padx=30)
        self.options_frame = ctk.CTkFrame(self.center, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=20)
        self.btns = []
        for i in range(4):
            btn = ctk.CTkButton(self.options_frame, text="", height=60, font=("Arial", 14), command=lambda idx=i: self.check_answer(idx), corner_radius=15)
            btn.pack(fill="x", pady=5)
            self.btns.append(btn)
        self.questions = []
        self.current_idx = 0
        self.correct_count = 0
        self.total_xp = 0
        self.score = 0
        self.start_quiz()

    def start_quiz(self):
        self.questions = []
        for _ in range(5):
            port = random.choice(list(TOOLS_DB.keys()))
            data = TOOLS_DB[port]
            q_type = random.choice(["tool", "port", "risk"])
            if q_type == "tool":
                q_text = f"Qual ferramenta é ideal para: {data['name']}?"
                ans = data['tool']
                wrongs = ["NMAP", "WIRESHARK", "BURPSUITE", "JOHN"]
            elif q_type == "port":
                q_text = f"Qual porta é padrão para: {data['name']}?"
                ans = str(port)
                wrongs = ["8080", "4444", "25", "53"]
            else:
                q_text = f"Qual o risco de: {data['name']}?"
                ans = "Alto" if port in [445, 22, 3306] else "Médio"
                wrongs = ["Baixo", "Nenhum", "Desconhecido"]
            opts = random.sample(wrongs, 3) + [ans]
            random.shuffle(opts)
            correct_idx = opts.index(ans)
            self.questions.append({
                'q_text': q_text,
                'options': opts,
                'correct': correct_idx,
                'user_answer': -1
            })
        self.current_idx = 0
        self.correct_count = 0
        self.total_xp = 0
        self.show_question()

    def show_question(self):
        if self.current_idx >= len(self.questions):
            self.show_results()
            return
        q = self.questions[self.current_idx]
        self.lbl_q.configure(text=q['q_text'])
        self.lbl_stats.configure(text=f"🎯 Questão {self.current_idx+1}/5 | Pontuação: {self.score}")
        for i, opt in enumerate(q['options']):
            self.btns[i].configure(text=opt, fg_color=COLOR_ACCENT_BLUE, state="normal")

    def check_answer(self, idx):
        q = self.questions[self.current_idx]
        q['user_answer'] = idx
        if idx == q['correct']:
            self.correct_count += 1
            self.score += 10
        self.current_idx += 1
        self.show_question()

    def show_results(self):
        self.total_xp = self.correct_count * 20
        for _ in range(self.correct_count):
            game_engine.add_xp(20)
        for w in self.center.winfo_children():
            w.destroy()
        result_frame = ctk.CTkFrame(self.center, fg_color=COLOR_CARD, corner_radius=20)
        result_frame.pack(pady=20, fill="both", expand=True, padx=20)
        ctk.CTkLabel(result_frame, text="QUIZ COMPLETO!", font=("Arial", 24, "bold"), text_color=COLOR_ACCENT_GREEN).pack(pady=20)
        ctk.CTkLabel(result_frame, text=f"Acertos: {self.correct_count}/5 | XP Ganho: {self.total_xp}", font=("Arial", 18), text_color="white").pack(pady=10)
        scroll = ctk.CTkScrollableFrame(result_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        for i, q in enumerate(self.questions):
            card = ctk.CTkFrame(scroll, fg_color="#1a1a1a", corner_radius=10)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=f"Questão {i+1}: {q['q_text']}", font=("Arial", 14, "bold"), text_color="white", wraplength=600, justify="left").pack(anchor="w", padx=10, pady=5)
            user_ans = q['options'][q['user_answer']] if q['user_answer'] != -1 else "Não respondeu"
            correct_ans = q['options'][q['correct']]
            color = COLOR_ACCENT_GREEN if q['user_answer'] == q['correct'] else "#ff5555"
            ctk.CTkLabel(card, text=f"Sua resposta: {user_ans}", font=("Arial", 12), text_color=color).pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Correta: {correct_ans}", font=("Arial", 12), text_color=COLOR_ACCENT_GOLD).pack(anchor="w", padx=10, pady=(0,5))
        ctk.CTkButton(result_frame, text="JOGAR NOVAMENTE", command=self.restart_quiz, fg_color=COLOR_ACCENT_BLUE, height=50).pack(pady=20)

    def restart_quiz(self):
        for w in self.center.winfo_children():
            w.destroy()
        self.question_card = ctk.CTkFrame(self.center, fg_color=COLOR_CARD, corner_radius=20, border_width=2, border_color=COLOR_ACCENT_BLUE)
        self.question_card.pack(pady=20, fill="x")
        self.lbl_q = ctk.CTkLabel(self.question_card, text="...", font=("Roboto", 20, "bold"), wraplength=600, text_color="white")
        self.lbl_q.pack(pady=30, padx=30)
        self.options_frame = ctk.CTkFrame(self.center, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=20)
        self.btns = []
        for i in range(4):
            btn = ctk.CTkButton(self.options_frame, text="", height=60, font=("Arial", 14), command=lambda idx=i: self.check_answer(idx), corner_radius=15)
            btn.pack(fill="x", pady=5)
            self.btns.append(btn)
        self.start_quiz()

# ==========================================
# 4. SIMULADOR DE MISSÃO
# ==========================================

class DifficultySelectorFrame(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, fg_color="transparent")
        self.cb = callback
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text="CONFIGURAÇÃO DE SIMULAÇÃO", font=("Arial", 24, "bold")).pack(pady=30)
        ctk.CTkButton(box, text="🟢 MODO GUIADO (Fácil)", command=lambda: self.cb("EASY"), height=50, width=350, fg_color="green").pack(pady=10)
        ctk.CTkButton(box, text="🟡 MODO PADRÃO (Médio)", command=lambda: self.cb("MEDIUM"), height=50, width=350, fg_color="orange").pack(pady=10)
        ctk.CTkButton(box, text="🔴 MODO REALISTA (Difícil)", command=lambda: self.cb("HARD"), height=50, width=350, fg_color="red").pack(pady=10)

class SimulatorFrame(ctk.CTkFrame):
    def __init__(self, parent, mission_data, difficulty, finish_callback):
        super().__init__(parent, fg_color="transparent")
        self.steps = mission_data['steps']
        self.idx = 0
        self.ip = mission_data['ip']
        self.diff = difficulty
        self.finish_cb = finish_callback
        self.history = [] 
        self.detection = 0
        self.current_round_options = []
        
        # --- FILA DE MENSAGENS PARA EVITAR SOBREPOSIÇÃO ---
        self.output_queue = []
        self.is_typing = False
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.hud = ctk.CTkFrame(self, height=60, fg_color="#000")
        self.hud.grid(row=0, sticky="ew")
        ctk.CTkLabel(self.hud, text=f"ALVO: {self.ip} | MODO: {difficulty}", text_color="cyan", font=("Consolas", 12)).pack(side="left", padx=20, pady=10)
        
        self.progress_frame = ctk.CTkFrame(self.hud, fg_color="transparent")
        self.progress_frame.pack(side="left", expand=True, padx=20)
        self.progress_dots = []
        for i in range(len(self.steps)):
            dot = ctk.CTkLabel(self.progress_frame, text="●", font=("Arial", 20), text_color="#333")
            dot.pack(side="left", padx=3)
            self.progress_dots.append(dot)
        
        self.lbl_det = ctk.CTkLabel(self.hud, text="DETECÇÃO IDS: 0%", text_color="green", font=("Consolas", 12, "bold"))
        self.lbl_det.pack(side="right", padx=20, pady=10)
        
        self.out = ctk.CTkTextbox(self, font=("Consolas", 14), fg_color="#0a0a0a", text_color="#0f0", wrap="word")
        self.out.grid(row=1, sticky="nsew", padx=10, pady=10)
        self.out.tag_config("teach", foreground="#00e5ff")
        self.out.tag_config("success", foreground=COLOR_ACCENT_GOLD)
        self.out.tag_config("fail", foreground="#ff5555")
        self.out.tag_config("info", foreground="#aaaaaa")
        self.out.tag_config("phase", foreground="cyan")
        self.out.tag_config("context", foreground="yellow")
        self.out.tag_config("options", foreground="green")
        self.out.tag_config("prompt", foreground="white")
        self.out.tag_config("user", foreground="white")
        self.log("CONEXÃO ESTABELECIDA...\n", animate=False)
        self.out.configure(state="disabled")

        self.inp_box = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.inp_box.grid(row=2, sticky="ew", padx=10, pady=10)
        self.lbl_hint = ctk.CTkLabel(self.inp_box, text="Aguardando comando...", text_color="gray", anchor="w")
        self.lbl_hint.pack(fill="x")
        self.entry = ctk.CTkEntry(self.inp_box, font=("Consolas", 14), fg_color="#222", border_width=0, height=40)
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.run_cmd)
        self.entry.bind("<KeyRelease>", self.check_hint)
        self.entry.focus()
        self.after(0, self.load_step)

    def log(self, text, end="\n", tag=None, animate=True):
        full_text = text + end
        
        if animate and game_engine.get_setting("animations"):
            self.output_queue.append((full_text, tag))
            self._process_queue()
        else:
            self.out.configure(state="normal")
            self.out.insert("end", full_text, tag)
            self.out.see("end")
            self.out.update_idletasks()
            self.out.configure(state="disabled")

    def _process_queue(self):
        if self.is_typing or not self.output_queue:
            return
            
        self.is_typing = True
        text, tag = self.output_queue.pop(0)
        self.type_text(text, tag)

    def type_text(self, text, tag, index=0):
        self.out.configure(state="normal")
        
        if index < len(text):
            self.out.insert("end", text[index], tag)
            self.out.see("end")
            # Recurso para próxima letra
            self.after(1, lambda: self.type_text(text, tag, index+1))
        else:
            self.out.configure(state="disabled")
            self.is_typing = False
            # Chama a próxima mensagem da fila (se houver)
            self.after(0, self._process_queue)

    def update_progress_trail(self):
        for i, dot in enumerate(self.progress_dots):
            if i < self.idx: dot.configure(text_color=COLOR_ACCENT_GREEN)
            elif i == self.idx:
                dot.configure(text_color="#004400")  # Dark green
                pulse_color(dot, "#004400", "#00ff00")  # Pulse between dark and neon green
            else: dot.configure(text_color="#333")

    def load_step(self):
        if self.idx >= len(self.steps):
            self.finish_cb(self.history, "Todos os objetivos da missão foram alcançados com sucesso.", True)
            return
        self.update_progress_trail()
        step = self.steps[self.idx]
        self.correct = step['correct'].replace("{ip}", self.ip)
        opts = [self.correct]
        for k in step.get('fail_logs', {}): opts.append(k.replace("{ip}", self.ip))
        dummies = [f"nmap -A {self.ip}", f"sqlmap -u mysql://{self.ip}", f"hydra -l root mysql://{self.ip}", f"telnet {self.ip} 3306", f"ssh {self.ip}", f"ping {self.ip}"]
        while len(opts) < 4:
            d = random.choice(dummies); 
            if d not in opts: opts.append(d)
        random.shuffle(opts)
        self.current_round_options = opts
        self.log(f"\n[FASE {self.idx+1}/{len(self.steps)}] {step['phase']}\n", tag="phase", animate=False)
        self.log(f"INTELIGÊNCIA: {step['context']}", tag="context", animate=False)
        self.log("VETORES DE ATAQUE DISPONÍVEIS:", tag="options", animate=False)
        for o in opts: self.log(f" > {o}", tag="options", animate=False)
        self.log(f"\nroot@kali:~# ", end="", tag="prompt", animate=False)

    def check_hint(self, event):
        if self.diff == "HARD":
            self.lbl_hint.configure(text="", text_color="#555")
            return
        txt = self.entry.get()
        if self.diff == "EASY":
            if self.correct.startswith(txt) and len(txt) > 0:
                self.lbl_hint.configure(text=f"...{self.correct[len(txt):]} (pode não ser a melhor opção)", text_color="green")
            else:
                self.lbl_hint.configure(text="Digite um comando...", text_color="gray")
        elif self.diff == "MEDIUM":
            if txt:
                for opt in self.current_round_options:
                    if opt.startswith(txt):
                        self.lbl_hint.configure(text=f"...{opt[len(txt):]}", text_color="yellow")
                        return
                self.lbl_hint.configure(text="Digite um comando...", text_color="gray")
            else:
                self.lbl_hint.configure(text="", text_color="#555")

    def run_cmd(self, event):
        cmd = self.entry.get().strip()
        self.entry.delete(0, "end")
        self.log(cmd, tag="user", animate=False)
        game_engine.add_command()
        step = self.steps[self.idx]
        if cmd == self.correct:
            self.history.append({"cmd": cmd, "status": "SUCCESS", "reason": f"[ANÁLISE]: {step['teach']}"})
            self.log(step['success_logs'].replace("{ip}", self.ip), tag="success", animate=False)
            self.log(f"\n[MENTOR] {step['teach']}", tag="teach", animate=False)
            self.idx += 1
            self.after(1500, self.load_step)
            return
        hit_fail = False
        for fail, data in step.get('fail_logs', {}).items():
            if cmd == fail.replace("{ip}", self.ip):
                self.history.append({"cmd": cmd, "status": "FAIL", "reason": data['msg']})
                if not self.update_detection(data['risk'], "Erro Tático"):
                    self.log(f"[!] {data['msg']}", tag="fail")
                    glitch_effect(self.out, 100)
                    self.log(f"\nroot@kali:~# ", end="", animate=False)
                hit_fail = True
                game_engine.add_error()
                break
        if not hit_fail:
            game_engine.add_error()
            self.history.append({"cmd": cmd, "status": "NEUTRAL", "reason": "Comando irrelevante."})
            if not self.update_detection(10, "Comando Inútil"):
                self.log("[!] Comando sem efeito no alvo.", tag="fail")
                glitch_effect(self.out, 100)
                self.log(f"\nroot@kali:~# ", end="", animate=False)

    def update_detection(self, amount, reason):
        self.detection += amount if self.diff != "EASY" else (amount // 2)
        if self.detection > 100: self.detection = 100
        color = "green"
        if self.detection > 50: color = "orange"
        if self.detection > 80: color = "red"; glitch_effect(self, 100)
        self.lbl_det.configure(text=f"DETECÇÃO IDS: {self.detection}%", text_color=color)
        if self.detection >= 100:
            self.finish_cb(self.history, f"Sua atividade foi detectada pelo Blue Team. {reason}", False)
            return True
        return False

class MissionFlowFrame(ctk.CTkFrame):
    def __init__(self, parent, mission_data, return_to_hub_callback):
        super().__init__(parent, fg_color="transparent")
        self.data = mission_data
        self.return_callback = return_to_hub_callback
        header = ctk.CTkFrame(self, height=60, fg_color="#111")
        header.pack(fill="x", side="top")
        ctk.CTkButton(header, text="⬅ ABORTAR MISSÃO", width=120, fg_color="#333", hover_color="#444", command=self.return_callback).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text=f"OPERAÇÃO: {mission_data['name'].upper()}", font=("Arial", 16, "bold"), text_color=COLOR_ACCENT_BLUE).pack(side="left", padx=20)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        self.show_difficulty()

    def show_difficulty(self):
        for w in self.content.winfo_children(): w.destroy()
        DifficultySelectorFrame(self.content, self.start_sim).pack(fill="both", expand=True)

    def start_sim(self, difficulty):
        for w in self.content.winfo_children(): w.destroy()
        SimulatorFrame(self.content, self.data, difficulty, self.show_report).pack(fill="both", expand=True)

    def show_report(self, history, msg, success):
        for w in self.content.winfo_children(): w.destroy()
        if success:
            xp_gain = self.data.get('xp_reward', 100) 
            game_engine.add_xp(xp_gain)
            try: self.master.master.update_sidebar_data()
            except: pass
        MissionReport(self.content, history, msg, success, self.return_callback, self.data['name']).pack(fill="both", expand=True)

# ==========================================
# 5. SANDBOX SYSTEM & TERMINAL
# ==========================================

class SimulatedFileSystem:
    """Sistema de arquivos simulado independente de SO"""
    def __init__(self):
        # Árvore de diretórios
        self.root = {
            "contents": {
                "bin": {"type": "dir", "contents": {}},
                "boot": {"type": "dir", "contents": {}},
                "dev": {"type": "dir", "contents": {}},
                "etc": {
                    "type": "dir",
                    "contents": {
                        "passwd": {"type": "file", "content": "root:x:0:0:root:/root:/bin/bash\nadmin:x:1000:1000:admin:/home/admin:/bin/bash"},
                        "shadow": {"type": "file", "content": "root:$6$hash...:19000:0:99999:7:::\nadmin:$6$hash...:19000:0:99999:7:::"},
                        "hostname": {"type": "file", "content": "kali-academy"},
                        "hosts": {"type": "file", "content": "127.0.0.1 localhost\n127.0.1.1 kali"}
                    }
                },
                "home": {
                    "type": "dir",
                    "contents": {
                        "admin": {
                            "type": "dir",
                            "contents": {
                                "user.txt": {"type": "file", "content": "FLAG{USER_ACCESS_GRANTED}\nParabéns! Você acessou a pasta home de outro usuário."},
                                "todo.list": {"type": "file", "content": "- Atualizar servidores\n- Verificar logs\n- Aprender Python"}
                            }
                        }
                    }
                },
                "root": {
                    "type": "dir",
                    "contents": {
                        "root.txt": {"type": "file", "content": "PARABÉNS! VOCÊ OBTEVE ACESSO ROOT!\n\nSe você está lendo isso, você navegou com sucesso pelo sistema de arquivos.\nFLAG{ROOT_PRIVILEGE_ESCALATION_SUCCESS}"},
                        "sandbox": {
                            "type": "dir",
                            "contents": {
                                "notes.txt": {"type": "file", "content": "Alvos: 192.168.1.10, 192.168.1.15"},
                                "exploit.py": {"type": "file", "content": "import socket\nprint('Exploit running...')"}
                            }
                        }
                    }
                },
                "var": {
                    "type": "dir",
                    "contents": {
                        "www": {
                            "type": "dir",
                            "contents": {
                                "html": {
                                    "type": "dir",
                                    "contents": {
                                        "index.php": {"type": "file", "content": "<?php echo 'Hello World'; ?>"},
                                        "secret_config.php": {"type": "file", "content": "<?php $db_pass = 'SuperSecretPass123'; ?>\n\nPARABÉNS! Você encontrou credenciais vazadas no servidor web.\nFLAG{WEB_CONFIG_LEAK_DISCOVERED}"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        self.current_path = "/root/sandbox"

    def get_current_path(self):
        return self.current_path

    def _normalize_path(self, path):
        """Normaliza caminhos e resolve .. e . manualmente"""
        if not path:
            return self.current_path

        # Define se é absoluto ou relativo
        if path.startswith("/"):
            parts = []
        else:
            parts = [p for p in self.current_path.split("/") if p]

        # Processa cada parte
        for part in path.split("/"):
            if not part or part == ".":
                continue
            elif part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)

        return "/" + "/".join(parts)

    def _get_node(self, path):
        """Navega no dicionário para encontrar o nó"""
        normalized_path = self._normalize_path(path)
        if normalized_path == "/":
            return self.root

        parts = [p for p in normalized_path.split("/") if p]
        current = self.root

        for part in parts:
            if "contents" in current and part in current["contents"]:
                current = current["contents"][part]
            else:
                raise FileNotFoundError(f"No such file or directory: {path}")

        return current

    def change_dir(self, path):
        target_path = self._normalize_path(path)
        node = self._get_node(target_path)
        if node.get("type") != "dir":
            raise NotADirectoryError(f"Not a directory: {path}")
        self.current_path = target_path

    def list_dir(self, path="."):
        target_path = self._normalize_path(path)
        node = self._get_node(target_path)
        if node.get("type") != "dir":
            raise NotADirectoryError(f"Not a directory: {path}")
        items = []
        for name, data in node.get("contents", {}).items():
            if data["type"] == "dir": items.append(f"{name}/")
            else: items.append(name)
        return sorted(items)

    def read_file(self, path):
        target_path = self._normalize_path(path)
        node = self._get_node(target_path)
        if node.get("type") != "file": raise IsADirectoryError(f"Is a directory: {path}")
        return node.get("content", "")

    def create_file(self, name):
        # Lógica simplificada: cria no diretório atual se não for caminho absoluto
        path = self._normalize_path(name)
        if "/" in name:
            parent_dir = name.rsplit("/", 1)[0]
            if not parent_dir: parent_dir = "/"
            filename = name.rsplit("/", 1)[1]
        else:
            parent_dir = self.current_path
            filename = name

        parent_node = self._get_node(parent_dir)
        parent_node["contents"][filename] = {"type": "file", "content": ""}

    def delete_node(self, name):
        path = self._normalize_path(name)
        # Separa pai e filho manualmente
        if "/" in path:
            parent_path = path.rsplit("/", 1)[0]
            if not parent_path: parent_path = "/"
            target_name = path.rsplit("/", 1)[1]
        else: # Nunca deve acontecer pois normalize coloca /
            return

        parent_node = self._get_node(parent_path)
        if target_name in parent_node["contents"]:
            del parent_node["contents"][target_name]
        else:
            raise FileNotFoundError(f"No such file: {name}")

    def create_dir(self, name):
        path = self._normalize_path(name)
        if "/" in name:
            parent_dir = name.rsplit("/", 1)[0]
            if not parent_dir: parent_dir = "/"
            dirname = name.rsplit("/", 1)[1]
        else:
            parent_dir = self.current_path
            dirname = name

        parent_node = self._get_node(parent_dir)
        parent_node["contents"][dirname] = {"type": "dir", "contents": {}}

    def remove_dir(self, name):
        path = self._normalize_path(name)
        if "/" in path:
            parent_path = path.rsplit("/", 1)[0]
            if not parent_path: parent_path = "/"
            target_name = path.rsplit("/", 1)[1]
        else:
            return

        parent_node = self._get_node(parent_path)
        if target_name in parent_node["contents"] and parent_node["contents"][target_name]["type"] == "dir":
            if not parent_node["contents"][target_name]["contents"]:  # Only if empty
                del parent_node["contents"][target_name]
            else:
                raise OSError(f"Directory not empty: {name}")
        else:
            raise FileNotFoundError(f"No such directory: {name}")

    def find_files(self, start_path=".", name="*"):
        """Simula find, retorna lista de caminhos"""
        results = []
        def recurse(current_path, node):
            for item_name, item_data in node.get("contents", {}).items():
                item_path = f"{current_path}/{item_name}" if current_path != "/" else f"/{item_name}"
                if name == "*" or name in item_name:
                    results.append(item_path)
                if item_data["type"] == "dir":
                    recurse(item_path, item_data)
        start_node = self._get_node(start_path)
        recurse(self._normalize_path(start_path), start_node)
        return results

    def grep_file(self, pattern, file_path):
        """Simula grep em arquivo"""
        content = self.read_file(file_path)
        lines = content.split('\n')
        matches = [line for line in lines if pattern in line]
        return '\n'.join(matches)

class SandboxFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Lista para o Autocomplete Simples
        self.COMMANDS = [
            "ls", "cat", "whoami", "clear", "nmap", "echo", "help",
            "pwd", "cd", "touch", "rm", "ping", "ip", "netcat",
            "history", "nano", "exit", "sudo", "grep", "hydra", "sqlmap", "msfconsole", "nikto",
            "mkdir", "rmdir", "find", "ps", "kill", "chmod", "wget", "curl", "ssh", "scp", "ftp"
        ]
        
        # LISTA DE EXEMPLOS COMPLETOS PARA SUGESTÃO
        self.COMMAND_EXAMPLES = [
            "nmap -sV -p- 192.168.1.10",
            "ping -c 4 8.8.8.8",
            "cat /etc/passwd",
            "ls -la /var/www/html",
            "hydra -l admin -P rockyou.txt ssh://192.168.1.5",
            "sqlmap -u 'http://site.com/index.php?id=1' --dbs",
            "netcat -lvnp 4444",
            "msfconsole -q",
            "nikto -h 192.168.1.10",
            "find / -name *.txt",
            "grep root /etc/passwd",
            "ssh root@192.168.1.10",
            "wget http://example.com/file.txt",
            "curl http://example.com"
        ]
        
        self.command_history = []
        self.fs = SimulatedFileSystem()
        
        # Controle de Threads e Fila de Mensagens
        self.stop_flag = False
        self.current_process = None
        self.output_queue = [] # NOVA: Fila para evitar colisão de texto
        self.is_typing = False # NOVA: Flag de ocupado
        
        # Cabeçalho
        header = ctk.CTkFrame(self, height=80, fg_color="#111")
        header.pack(fill="x", side="top", pady=(0, 10))
        
        ctk.CTkLabel(header, text="💻 TERMINAL SANDBOX", font=("Arial", 22, "bold"), text_color="#00ff00").pack(side="left", padx=20)
        
        # Botão STOP (Visível apenas quando comando roda)
        self.stop_btn = ctk.CTkButton(header, text="🛑 PARAR (Ctrl+C)", fg_color="#ff4444", hover_color="#cc0000",
                                      command=self.stop_command, width=120, height=30, font=("Arial", 11, "bold"))
        self.stop_btn.pack(side="right", padx=20)
        self.stop_btn.pack_forget() # Esconde inicialmente

        # Console
        self.console = ctk.CTkTextbox(self, font=("Consolas", 14), fg_color="#0a0a0a", text_color="#00ff00", wrap="word")
        self.console.pack(fill="both", expand=True, padx=10, pady=5)
        self.console.insert("end", "KALI LINUX ROLLING [Versão 2024.1]\nType 'help' for available commands.\n\nroot@kali:~/sandbox# ")
        self.console.configure(state="disabled")
        self.console.update()

        # Área de Input e Sugestões
        self.input_area = ctk.CTkFrame(self, fg_color="transparent")
        self.input_area.pack(fill="x", padx=10, pady=10)

        # Label de Sugestões (Aparece acima do input)
        self.lbl_suggestions = ctk.CTkLabel(self.input_area, text="", font=("Consolas", 12, "italic"), text_color="#555", anchor="w")
        self.lbl_suggestions.pack(fill="x", padx=10)

        # Linha de comando
        input_box = ctk.CTkFrame(self.input_area, height=40, fg_color="transparent")
        input_box.pack(fill="x")
        
        self.prompt_label = ctk.CTkLabel(input_box, text="root@kali:~/sandbox#", font=("Consolas", 14, "bold"), text_color="#00ff00")
        self.prompt_label.pack(side="left")
        
        self.entry = ctk.CTkEntry(input_box, font=("Consolas", 14), fg_color="#222", border_width=0)
        self.entry.pack(side="left", fill="x", expand=True, padx=10)
        
        # Bindings (Teclas)
        self.entry.bind("<Return>", self.run_command)
        self.entry.bind("<KeyRelease>", self.update_suggestions) 
        self.entry.bind("<Tab>", self.auto_complete)             
        self.entry.bind("<Control-c>", self.stop_command)        
        self.entry.focus()

    def log(self, text):
        # Limpeza de buffer antigo
        try:
            lines = int(self.console.index("end-1c").split('.')[0])
            if lines > 500:
                self.console.configure(state="normal")
                self.console.delete("1.0", f"{lines-500}.0")
                self.console.configure(state="disabled")
        except: pass
        
        # Se tem animação, usa a FILA
        if game_engine.get_setting("animations"):
            self.output_queue.append(text + "\n")
            self._process_queue()
        else:
            self.console.configure(state="normal")
            self.console.insert("end", text + "\n")
            self.console.see("end")
            self.console.update_idletasks()
            self.console.configure(state="disabled")

    def _process_queue(self):
        # Se já estiver escrevendo ou fila vazia, sai
        if self.is_typing or not self.output_queue:
            return
            
        self.is_typing = True
        next_text = self.output_queue.pop(0)
        self.type_text(next_text)

    def type_text(self, text, index=0):
        self.console.configure(state="normal")
        
        if index < len(text):
            self.console.insert("end", text[index])
            self.console.see("end")
            # Recurso para próxima letra
            self.after(1, lambda: self.type_text(text, index+1))
        else:
            self.console.configure(state="disabled")
            self.is_typing = False
            # Tenta processar próxima mensagem da fila
            self.after(0, self._process_queue)

    def update_suggestions(self, event):
        if event.keysym in ["Return", "BackSpace", "Tab", "Control_L"]: return
        txt = self.entry.get().strip()
        if not txt:
            self.lbl_suggestions.configure(text="")
            return
        
        # Filtra exemplos completos
        matches = [ex for ex in self.COMMAND_EXAMPLES if ex.startswith(txt)]
        
        if matches:
            suggestion_text = "Exemplos: " + "  |  ".join(matches[:3])
            if len(matches) > 3: suggestion_text += "  ..."
            self.lbl_suggestions.configure(text=suggestion_text, text_color="#00aa00")
        else:
            # Fallback para comandos simples
            matches_simple = [c for c in self.COMMANDS if c.startswith(txt)]
            if matches_simple:
                self.lbl_suggestions.configure(text="Comandos: " + " ".join(matches_simple[:5]), text_color="#555")
            else:
                self.lbl_suggestions.configure(text="")

    def auto_complete(self, event):
        txt = self.entry.get().strip()
        if not txt: return "break"
        
        matches = [c for c in self.COMMANDS if c.startswith(txt)]
        if len(matches) == 1:
            self.entry.delete(0, "end")
            self.entry.insert(0, matches[0] + " ")
            self.lbl_suggestions.configure(text="")
        return "break" 

    def update_prompt(self):
        cwd = self.fs.get_current_path().replace("/root", "~")
        self.prompt_label.configure(text=f"root@kali:{cwd}#")

    def stop_command(self, event=None):
        """Interrompe comandos threaded"""
        self.stop_flag = True
        self.stop_btn.pack_forget()
        self.log("^C")

    def run_command(self, event):
        cmd_line = self.entry.get().strip()
        self.entry.delete(0, "end")
        self.lbl_suggestions.configure(text="")
        
        if not cmd_line: return
        
        self.command_history.append(cmd_line)
        self.log(f"{self.prompt_label.cget('text')} {cmd_line}")
        
        parts = cmd_line.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # --- COMANDOS DO SISTEMA ---
        try:
            if command == "help":
                self.log("COMANDOS DISPONÍVEIS:\n" + ", ".join(sorted(self.COMMANDS)))
            
            elif command == "ls":
                target = args[0] if args else "."
                self.log("  ".join(self.fs.list_dir(target)))
                
            elif command == "cd":
                target = args[0] if args else "/root"
                self.fs.change_dir(target)
                self.update_prompt()
                
            elif command == "pwd":
                self.log(self.fs.get_current_path())
                
            elif command == "cat":
                if args:
                    content = self.fs.read_file(args[0])
                    if "FLAG{" in content:
                        # Create a temporary label to decodify the flag
                        temp_label = ctk.CTkLabel(self, text="")
                        temp_label.pack_forget()  # Hide it
                        decodify_text(temp_label, content, duration=1.0)
                        # After decodify, log the content
                        self.after(1100, lambda: self.log(content))  # Wait for decodify to finish
                        self.after(1100, lambda: temp_label.destroy())
                    else:
                        self.log(content)
                else: self.log("Uso: cat [arquivo]")
                
            elif command == "touch":
                if args: self.fs.create_file(args[0]); self.log("")
                else: self.log("Uso: touch [arquivo]")
                
            elif command == "rm":
                if args: self.fs.delete_node(args[0]); self.log("")
                else: self.log("Uso: rm [arquivo]")
                
            elif command == "whoami":
                self.log("root")
                
            elif command == "clear":
                self.console.configure(state="normal")
                self.console.delete("1.0", "end")
                self.console.configure(state="disabled")
            
            # --- COMANDOS DE REDE/HACKING (SIMULADOS) ---
            
            elif command == "ping":
                if args: self.start_threaded(self._ping_thread, args[0])
                else: self.log("Uso: ping [host]")
                
            elif command == "nmap":
                if args: self.start_threaded(self._nmap_thread, args[0])
                else: self.log("Uso: nmap [opções] [alvo]")
                
            elif command == "hydra":
                self.start_threaded(self._hydra_thread, None)
                
            elif command == "sqlmap":
                self.start_threaded(self._sqlmap_thread, None)
            
            elif command == "msfconsole":
                self.log("Iniciando Metasploit Framework...")
                self.log("msf6 > (Simulação interativa em desenvolvimento)")
                
            elif command == "nikto":
                self.start_threaded(self._nikto_thread, args[0] if args else "localhost")
                
            elif command in ["ip", "ifconfig"]:
                self.log("eth0: flags=4163<UP,BROADCAST,RUNNING>  mtu 1500")
                self.log("        inet 10.10.14.5  netmask 255.255.255.0")
                self.log("        ether 00:0c:29:1f:3a:4b")

            elif command == "mkdir":
                if args: self.fs.create_dir(args[0]); self.log("")
                else: self.log("Uso: mkdir [diretório]")

            elif command == "rmdir":
                if args: self.fs.remove_dir(args[0]); self.log("")
                else: self.log("Uso: rmdir [diretório]")

            elif command == "find":
                start = args[0] if args else "."
                name = args[1] if len(args) > 1 else "*"
                results = self.fs.find_files(start, name)
                self.log("\n".join(results))

            elif command == "grep":
                if len(args) >= 2:
                    pattern = args[0]
                    file_path = args[1]
                    matches = self.fs.grep_file(pattern, file_path)
                    self.log(matches)
                else: self.log("Uso: grep [padrão] [arquivo]")

            elif command == "ps":
                self.log("PID   TTY      TIME CMD")
                self.log("1     ?        00:00:01 init")
                self.log("123   pts/0    00:00:00 bash")
                self.log("456   pts/0    00:00:00 python")

            elif command == "kill":
                if args: self.log(f"Processo {args[0]} terminado.")
                else: self.log("Uso: kill [PID]")

            elif command == "chmod":
                if args: self.log(f"Permissões alteradas para {args[0]}")
                else: self.log("Uso: chmod [permissões] [arquivo]")

            elif command == "wget":
                if args: self.log(f"Baixando {args[0]}... Concluído.")
                else: self.log("Uso: wget [URL]")

            elif command == "curl":
                if args: self.log(f"Resposta de {args[0]}: HTTP 200 OK")
                else: self.log("Uso: curl [URL]")

            elif command == "ssh":
                if args: self.log(f"Conectando a {args[0]}... Conexão estabelecida.")
                else: self.log("Uso: ssh [user@host]")

            elif command == "scp":
                if len(args) >= 2: self.log(f"Copiando {args[0]} para {args[1]}... Concluído.")
                else: self.log("Uso: scp [origem] [destino]")

            elif command == "ftp":
                if args: self.log(f"Conectando ao FTP {args[0]}... Pronto.")
                else: self.log("Uso: ftp [host]")

            else:
                self.log(f"bash: {command}: comando não encontrado")
                
        except Exception as e:
            self.log(str(e))
        
        return "break"

    # --- LÓGICA DE THREADS E SIMULAÇÃO ---

    def start_threaded(self, func, arg):
        self.stop_flag = False
        self.stop_btn.pack(side="right", padx=20) # Mostra botão STOP
        t = threading.Thread(target=func, args=(arg,) if arg else ())
        t.daemon = True
        t.start()

    def _ping_thread(self, target):
        self.after(0, lambda: self.log(f"PING {target} ({target}) 56(84) bytes of data."))
        seq = 1
        while not self.stop_flag and seq < 100: # Loop infinito até STOP
            time.sleep(1)
            if self.stop_flag: break
            ms = random.randint(10, 90)
            # Closure correta para seq e ms
            self.after(0, lambda s=seq, m=ms: self.log(f"64 bytes from {target}: icmp_seq={s} ttl=64 time=0.0{m} ms"))
            seq += 1
        self.after(0, lambda: self.log(f"\n--- {target} ping statistics ---"))
        self.after(0, lambda: self.stop_btn.pack_forget())

    def _nmap_thread(self, target):
        self.after(0, lambda: self.log(f"Starting Nmap 7.94 at {time.strftime('%Y-%m-%d %H:%M')}"))
        time.sleep(1)
        self.after(0, lambda: self.log(f"Nmap scan report for {target}"))
        self.after(0, lambda: self.log("Host is up (0.0023s latency)."))
        self.after(0, lambda: self.log("Not shown: 997 closed tcp ports"))
        time.sleep(1)
        if self.stop_flag:
            self.after(0, lambda: self.log("\nScan aborted."))
            self.after(0, lambda: self.stop_btn.pack_forget())
            return

        self.after(0, lambda: self.log("PORT     STATE SERVICE"))
        self.after(0, lambda: self.log("22/tcp   open  ssh"))
        self.after(0, lambda: self.log("80/tcp   open  http"))
        self.after(0, lambda: self.log("3306/tcp open  mysql"))
        self.after(0, lambda: self.log(f"\nNmap done: 1 IP address scanned in {random.randint(2,5)}.45 seconds"))
        self.after(0, lambda: self.stop_btn.pack_forget())

    def _hydra_thread(self):
        self.after(0, lambda: self.log("Hydra v9.1 (c) 2023 by van Hauser/THC"))
        self.after(0, lambda: self.log("[DATA] attacking service ssh on port 22"))
        for i in range(1, 6):
            if self.stop_flag: break
            time.sleep(0.8)
            # Closure correta para i (idx)
            self.after(0, lambda idx=i: self.log(f"[ATTEMPT] target 192.168.1.10 - login \"root\" - pass \"123456\" - {idx} of 100"))
        if not self.stop_flag:
            self.after(0, lambda: self.log("[DATA] 1 valid password found"))
            # Reveal password with decodify
            temp_label = ctk.CTkLabel(self, text="")
            temp_label.pack_forget()
            decodify_text(temp_label, "SuperSecretPass123", duration=1.0)
            self.after(1100, lambda: self.log("Password: SuperSecretPass123"))
            self.after(1100, lambda: temp_label.destroy())
        self.after(0, lambda: self.stop_btn.pack_forget())

    def _sqlmap_thread(self):
        self.after(0, lambda: self.log("sqlmap identified the following injection point(s) with a total of 56 HTTP(s) requests:"))
        time.sleep(1)
        self.after(0, lambda: self.log("---"))
        self.after(0, lambda: self.log("Parameter: id (GET)"))
        self.after(0, lambda: self.log("    Type: boolean-based blind"))
        self.after(0, lambda: self.log("    Title: AND boolean-based blind - WHERE or HAVING clause"))
        time.sleep(1)
        if not self.stop_flag:
            self.after(0, lambda: self.log("    Payload: id=1 AND 2561=2561"))
            self.after(0, lambda: self.log("---"))
            self.after(0, lambda: self.log("[INFO] the back-end DBMS is MySQL"))
        self.after(0, lambda: self.stop_btn.pack_forget())

    def _nikto_thread(self, target):
        self.after(0, lambda: self.log(f"- Nikto v2.1.6"))
        self.after(0, lambda: self.log(f"+ Target IP.:          {target}"))
        time.sleep(1)
        self.after(0, lambda: self.log(f"+ Server: Apache/2.4.49"))
        if not self.stop_flag:
            time.sleep(1)
            self.after(0, lambda: self.log(f"+ /admin/: Admin interface found."))
            self.after(0, lambda: self.log(f"+ /config.php: Configuration file found."))
        self.after(0, lambda: self.stop_btn.pack_forget())