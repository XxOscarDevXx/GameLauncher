import customtkinter as ctk
from tkinter import filedialog, Menu
from PIL import Image
import os
import subprocess
import threading
import time
import random
from game_manager import GameManager
from settings_manager import SettingsManager
from metadata_fetcher import fetch_metadata
from music_manager import MusicManager
from sound_manager import SoundManager
from tray_icon import TrayIcon
from controller_manager import ControllerManager
from theme_editor import ThemeEditorDialog
from chat_client import ChatClient
from friends_ui import FriendsPanel
import cv2

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class EditGameDialog(ctk.CTkToplevel):
    def __init__(self, parent, game_data, settings_manager, save_callback):
        super().__init__(parent)
        self.game_data = game_data
        self.settings_manager = settings_manager
        self.save_callback = save_callback
        
        self.title(settings_manager.get_text("edit"))
        self.geometry("400x500")
        
        # Name
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Name")
        self.name_entry.insert(0, game_data["name"])
        self.name_entry.pack(pady=10, padx=20, fill="x")
        
        # Description
        ctk.CTkLabel(self, text=settings_manager.get_text("description")).pack(anchor="w", padx=20)
        self.desc_textbox = ctk.CTkTextbox(self, height=100)
        self.desc_textbox.insert("0.0", game_data.get("description", ""))
        self.desc_textbox.pack(pady=5, padx=20, fill="x")

        # Categories
        ctk.CTkLabel(self, text=settings_manager.get_text("categories")).pack(anchor="w", padx=20)
        self.cat_entry = ctk.CTkEntry(self, placeholder_text="Action, RPG, Indie (comma separated)")
        self.cat_entry.insert(0, ", ".join(game_data.get("categories", [])))
        self.cat_entry.pack(pady=5, padx=20, fill="x")

        # Launch Arguments
        ctk.CTkLabel(self, text=settings_manager.get_text("launch_args")).pack(anchor="w", padx=20)
        self.args_entry = ctk.CTkEntry(self, placeholder_text="-windowed -nointro")
        self.args_entry.insert(0, game_data.get("launch_args", ""))
        self.args_entry.pack(pady=5, padx=20, fill="x")
        
        # Fetch Button
        self.fetch_btn = ctk.CTkButton(self, text=settings_manager.get_text("fetch_metadata"), command=self.fetch_data)
        self.fetch_btn.pack(pady=5)
        
        # Icon Preview
        self.icon_path = game_data["icon"]
        self.icon_label = ctk.CTkLabel(self, text="Icon Preview")
        self.icon_label.pack(pady=10)
        self.update_icon_preview()
        
        # Save/Cancel
        self.save_btn = ctk.CTkButton(self, text=settings_manager.get_text("save"), command=self.save)
        self.save_btn.pack(pady=10)
        
    def update_icon_preview(self):
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                pil_image = Image.open(self.icon_path)
                img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(60, 60))
                self.icon_label.configure(image=img, text="")
            except:
                self.icon_label.configure(text="Invalid Icon")
                
    def fetch_data(self):
        name = self.name_entry.get()
        data = fetch_metadata(name)
        if data:
            self.desc_textbox.delete("0.0", "end")
            self.desc_textbox.insert("0.0", data["description"])
            
            if "genres" in data and data["genres"]:
                current_cats = [c.strip() for c in self.cat_entry.get().split(",") if c.strip()]
                new_cats = list(set(current_cats + data["genres"]))
                self.cat_entry.delete(0, "end")
                self.cat_entry.insert(0, ", ".join(new_cats))
            
    def save(self):
        new_name = self.name_entry.get()
        new_desc = self.desc_textbox.get("0.0", "end").strip()
        new_cats = [c.strip() for c in self.cat_entry.get().split(",") if c.strip()]
        new_args = self.args_entry.get()
        self.save_callback(self.game_data["path"], new_name, new_desc, self.icon_path, new_cats, new_args)
        self.destroy()

class GameCard(ctk.CTkFrame):
    def __init__(self, master, game_data, launch_callback, settings_manager, favorite_callback, edit_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.game_data = game_data
        self.launch_callback = launch_callback
        self.settings_manager = settings_manager
        self.favorite_callback = favorite_callback
        self.edit_callback = edit_callback
        
        # Style
        # Style
        self.configure(fg_color=("gray85", "gray17"), corner_radius=10)
        self.pack(pady=8, padx=15, fill="x", expand=True)
        
        # Icon
        self.icon_image = None
        if game_data["icon"] and os.path.exists(game_data["icon"]):
            try:
                pil_image = Image.open(game_data["icon"])
                self.icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(40, 40))
            except Exception as e:
                print(f"Error loading icon: {e}")
        
        # Layout
        self.grid_columnconfigure(2, weight=1)
        
        # Icon Label
        self.icon_label = ctk.CTkLabel(self, text="", image=self.icon_image)
        self.icon_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Favorite Button (Star)
        fav_text = "★" if game_data.get("favorite") else "☆"
        fav_color = "gold" if game_data.get("favorite") else "gray"
        self.fav_btn = ctk.CTkButton(self, text=fav_text, width=30, fg_color="transparent", text_color=fav_color, font=("Arial", 20), command=self.toggle_fav)
        self.fav_btn.grid(row=0, column=1, padx=0)
        
        # Info Frame
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=2, padx=10, sticky="w")
        
        # Name Label
        self.name_label = ctk.CTkLabel(self.info_frame, text=game_data["name"], font=("Roboto", 16, "bold"))
        self.name_label.pack(anchor="w")
        
        # Play Time Label
        hours = game_data.get("play_time", 0) / 3600
        time_text = f"{self.settings_manager.get_text('time_played')}: {hours:.1f}{self.settings_manager.get_text('hours')}"
        self.time_label = ctk.CTkLabel(self.info_frame, text=time_text, font=("Roboto", 12), text_color="gray60")
        self.time_label.pack(anchor="w")
        
        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=0, column=3, padx=10)

        # Edit Button
        self.edit_btn = ctk.CTkButton(self.btn_frame, text="✎", width=30, fg_color="transparent", command=self.edit_game)
        self.edit_btn.pack(side="left", padx=5)
        
        # Play Button
        self.play_btn = ctk.CTkButton(self.btn_frame, text=self.settings_manager.get_text("play"), command=self.launch_game, width=80, corner_radius=20, hover_color=("green", "darkgreen"))
        self.play_btn.pack(side="left")

        # Bind Sounds
        self.fav_btn.bind("<Enter>", lambda e: master.master.master.sound_manager.play("hover"))
        self.fav_btn.bind("<Button-1>", lambda e: master.master.master.sound_manager.play("click"), add="+")
        
        self.edit_btn.bind("<Enter>", lambda e: master.master.master.sound_manager.play("hover"))
        self.edit_btn.bind("<Button-1>", lambda e: master.master.master.sound_manager.play("click"), add="+")
        
        self.play_btn.bind("<Enter>", lambda e: master.master.master.sound_manager.play("hover"))
        self.play_btn.bind("<Button-1>", lambda e: master.master.master.sound_manager.play("launch"), add="+")

    def launch_game(self):
        self.launch_callback(self.game_data["path"])
        
    def toggle_fav(self):
        self.favorite_callback(self.game_data["path"])
        
    def edit_game(self):
        self.edit_callback(self.game_data)
    
    def update_text(self):
        self.play_btn.configure(text=self.settings_manager.get_text("play"))
        hours = self.game_data.get("play_time", 0) / 3600
        time_text = f"{self.settings_manager.get_text('time_played')}: {hours:.1f}{self.settings_manager.get_text('hours')}"
        self.time_label.configure(text=time_text)

class GameGridCard(ctk.CTkFrame):
    def __init__(self, master, game_data, launch_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.game_data = game_data
        self.launch_callback = launch_callback
        
        self.configure(fg_color=("gray85", "gray17"), corner_radius=15)
        
        # Icon
        self.icon_image = None
        if game_data["icon"] and os.path.exists(game_data["icon"]):
            try:
                pil_image = Image.open(game_data["icon"])
                self.icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(100, 100))
            except:
                pass
        
        self.icon_label = ctk.CTkButton(self, text="", image=self.icon_image, fg_color="transparent", hover_color=("gray70", "gray30"), command=self.launch_game, width=120, height=120, corner_radius=15)
        self.icon_label.pack(pady=(15, 0))
        
        self.name_label = ctk.CTkLabel(self, text=game_data["name"], font=("Roboto", 14, "bold"), wraplength=120)
        self.name_label.pack(pady=(5, 10))
        
    def launch_game(self):
        self.launch_callback(self.game_data["path"])

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings_manager, refresh_callback):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.refresh_callback = refresh_callback
        self.title(settings_manager.get_text("settings"))
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Language
        ctk.CTkLabel(self, text=settings_manager.get_text("language"), font=("Roboto", 14)).pack(pady=(20, 5))
        current_lang = "English" if settings_manager.get_setting("language") == "en" else "Spanish"
        self.lang_option = ctk.CTkOptionMenu(self, values=["English", "Spanish"], command=self.change_language)
        self.lang_option.set(current_lang)
        self.lang_option.pack(pady=5)
        
        # Theme
        ctk.CTkLabel(self, text=settings_manager.get_text("theme"), font=("Roboto", 14)).pack(pady=(20, 5))
        current_theme = settings_manager.get_setting("theme", "dark-blue")
        theme_map = {"dark-blue": "Dark Blue", "blue": "Blue", "green": "Green"}
        rev_theme_map = {v: k for k, v in theme_map.items()}
        
        self.theme_option = ctk.CTkOptionMenu(
            self, 
            values=["Dark Blue", "Blue", "Green"],
            command=lambda c: self.change_theme(rev_theme_map[c])
        )
        self.theme_option.set(theme_map.get(current_theme, "Dark Blue"))
        self.theme_option.pack(pady=5)

        # Theme Editor Button
        ctk.CTkButton(self, text=settings_manager.get_text("theme_editor"), command=self.open_theme_editor).pack(pady=10)

        # Startup Video
        ctk.CTkLabel(self, text=settings_manager.get_text("startup_video"), font=("Roboto", 14)).pack(pady=(20, 5))
        self.video_label = ctk.CTkLabel(self, text=os.path.basename(settings_manager.get_setting("startup_video", "")) or "None")
        self.video_label.pack(pady=5)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=5)
        
        ctk.CTkButton(btn_frame, text=settings_manager.get_text("select_video"), command=self.select_video, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text=settings_manager.get_text("remove_video"), command=self.remove_video, width=100, fg_color="red", hover_color="darkred").pack(side="left", padx=5)

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Video", "*.mp4")])
        if file_path:
            self.settings_manager.set_setting("startup_video", file_path)
            self.video_label.configure(text=os.path.basename(file_path))

    def remove_video(self):
        self.settings_manager.set_setting("startup_video", "")
        self.video_label.configure(text="None")

    def open_theme_editor(self):
        ThemeEditorDialog(self, self.settings_manager, self.apply_custom_theme)

    def apply_custom_theme(self, theme_name):
        self.settings_manager.set_setting("theme", theme_name)
        if theme_name == "custom":
            custom_theme_path = os.path.join("themes", "custom.json")
            if os.path.exists(custom_theme_path):
                ctk.set_default_color_theme(custom_theme_path)
        else:
            ctk.set_default_color_theme(theme_name)
        # Reload UI
        self.refresh_callback()
        
    def change_language(self, choice):
        lang_code = "en" if choice == "English" else "es"
        self.settings_manager.set_setting("language", lang_code)
        self.refresh_callback()
        self.title(self.settings_manager.get_text("settings"))
        
    def change_theme(self, theme_code):
        self.settings_manager.set_setting("theme", theme_code)
        ctk.set_default_color_theme(theme_code)
        self.refresh_callback()

class MusicDialog(ctk.CTkToplevel):
    def __init__(self, parent, music_manager, settings_manager):
        super().__init__(parent)
        self.music_manager = music_manager
        self.settings_manager = settings_manager
        self.title(settings_manager.get_text("music_player"))
        self.geometry("300x400")
        
        # Controls
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(pady=10, fill="x")
        
        self.play_btn = ctk.CTkButton(self.controls_frame, text="⏯", width=40, command=self.toggle_play)
        self.play_btn.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(self.controls_frame, text="⏭", width=40, command=self.next_track)
        self.next_btn.pack(side="left", padx=10)
        
        self.add_btn = ctk.CTkButton(self.controls_frame, text="+", width=40, command=self.add_music)
        self.add_btn.pack(side="right", padx=10)
        
        # Playlist
        self.playlist_frame = ctk.CTkScrollableFrame(self, label_text="Playlist")
        self.playlist_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_playlist()
        
    def refresh_playlist(self):
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()
            
        playlist = self.music_manager.get_playlist()
        if not playlist:
            ctk.CTkLabel(self.playlist_frame, text=self.settings_manager.get_text("no_music")).pack(pady=20)
            return
            
        for i, track in enumerate(playlist):
            btn = ctk.CTkButton(self.playlist_frame, text=track, command=lambda idx=i: self.play_track(idx), fg_color="transparent", border_width=1)
            btn.pack(fill="x", pady=2)
            
    def toggle_play(self):
        self.music_manager.pause()
        
    def next_track(self):
        self.music_manager.next_track()
        
    def play_track(self, index):
        self.music_manager.play(index)
        
    def add_music(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if file_path:
            self.music_manager.add_music(file_path)
            self.refresh_playlist()

class GameLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Fix Taskbar Icon
        try:
            import ctypes
            myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass

        self.game_manager = GameManager()
        self.settings_manager = SettingsManager()
        self.music_manager = MusicManager()
        self.sound_manager = SoundManager()
        
        self.chat_client = ChatClient(on_message=self.on_chat_message)
        self.friends_panel = None
        self.username = None
        
        # Apply saved theme
        saved_theme = self.settings_manager.get_setting("theme", "dark-blue")
        if saved_theme == "custom":
            custom_theme_path = os.path.join("themes", "custom.json")
            if os.path.exists(custom_theme_path):
                ctk.set_default_color_theme(custom_theme_path)
            else:
                ctk.set_default_color_theme("dark-blue")
        else:
            ctk.set_default_color_theme(saved_theme)
        
        self.title(self.settings_manager.get_text("window_title"))
        self.title(self.settings_manager.get_text("window_title"))
        self.geometry("800x600")
        
        # Set Window Icon
        icon_path = os.path.join("icons", "app_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        # Check for startup video
        startup_video = self.settings_manager.get_setting("startup_video", "")
        if startup_video and os.path.exists(startup_video):
            self.play_startup_video(startup_video)
        else:
            self.after(0, lambda: self.state('zoomed')) # Maximize on startup
        
        self.settings_window = None
        self.music_window = None
        
        # System Tray
        self.tray_icon = TrayIcon(icon_path if os.path.exists(icon_path) else "icon.ico", self.restore_from_tray, self.quit_app)
        self.tray_icon.start()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # Controller
        self.controller = ControllerManager(self.handle_controller_input)
        
        self.view_mode = "list" # or "grid"
        self.current_category = "All"

        # Layout
        self.grid_rowconfigure(2, weight=1) # Row 2 is the main content
        self.grid_columnconfigure(0, weight=1) # Main content column
        self.grid_columnconfigure(1, weight=0) # Chat column (fixed width)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text=self.settings_manager.get_text("my_games"), font=("Roboto", 20, "bold"))
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_games)
        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text=self.settings_manager.get_text("search_placeholder"), textvariable=self.search_var, width=150)
        self.search_entry.pack(side="left", padx=20, pady=15)
        
        # Settings Button
        self.settings_btn = self.create_header_button("settings.png", "⚙️", self.open_settings)
        self.settings_btn.pack(side="right", padx=(5, 20), pady=15)
        
        # Roulette Button
        self.roulette_btn = self.create_header_button("roulette.png", "🎲", self.spin_wheel)
        self.roulette_btn.pack(side="right", padx=5, pady=15)
        
        # Music Button
        self.music_btn = self.create_header_button("music.png", "🎵", self.open_music)
        self.music_btn.pack(side="right", padx=5, pady=15)

        # Chat Button
        self.chat_btn = self.create_header_button("chat.png", "💬", self.toggle_chat)
        self.chat_btn.pack(side="right", padx=5, pady=15)

        self.add_btn = ctk.CTkButton(self.header_frame, text=self.settings_manager.get_text("add_game"), command=self.add_game_dialog, width=100)
        self.add_btn.pack(side="right", padx=5, pady=15)

        # View Toggle
        self.view_btn = self.create_header_button("grid.png", "▦", self.toggle_view)
        self.view_btn.pack(side="right", padx=5, pady=15)

        # Categories
        self.category_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.category_frame.grid(row=1, column=0, sticky="ew")
        self.category_frame.grid_columnconfigure(0, weight=1) # Center content
        
        self.categories = ["All"] + self.game_manager.get_categories()
        self.category_seg = ctk.CTkSegmentedButton(self.category_frame, values=self.categories, command=self.change_category)
        self.category_seg.set("All")
        self.category_seg.pack(pady=5)
        
        # Game List
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text=self.settings_manager.get_text("library"))
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.game_cards = []
        self.load_game_list()

    def bind_sounds(self, widget):
        widget.bind("<Enter>", lambda e: self.sound_manager.play("hover"))
        widget.bind("<Button-1>", lambda e: self.sound_manager.play("click"), add="+")

    def create_header_button(self, icon_name, fallback_text, command):
        icon_path = os.path.join("icons", icon_name)
        image = None
        if os.path.exists(icon_path):
             try:
                pil_image = Image.open(icon_path)
                image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(20, 20))
             except:
                 pass
        
        btn = ctk.CTkButton(
            self.header_frame, 
            text="" if image else fallback_text, 
            image=image,
            width=30, 
            command=command,
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        self.bind_sounds(btn)
        return btn

    def load_game_list(self, query=""):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.game_cards = []
            
        games = self.game_manager.get_games()
        
        # Filter by Category
        if self.current_category != "All":
            games = [g for g in games if self.current_category in g.get("categories", [])]

        # Filter by Search
        if query:
            games = [g for g in games if query.lower() in g["name"].lower()]
        
        if not games:
            self.empty_label = ctk.CTkLabel(self.scrollable_frame, text=self.settings_manager.get_text("no_games"), text_color="gray50")
            self.empty_label.pack(pady=50)
            return

        if self.view_mode == "list":
            for game in games:
                card = GameCard(
                    self.scrollable_frame, 
                    game, 
                    self.launch_game, 
                    self.settings_manager,
                    self.toggle_favorite,
                    self.open_edit_dialog
                )
                card.pack(pady=5, padx=5, fill="x")
                self.game_cards.append(card)
        else:
            self.load_game_grid(games)

    def load_game_grid(self, games):
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)
        row = 0
        col = 0
        for game in games:
            card = GameGridCard(self.scrollable_frame, game, self.launch_game)
            card.grid(row=row, column=col, padx=10, pady=10)
            self.game_cards.append(card)
            col += 1
            if col > 2: # 3 columns
                col = 0
                row += 1

    def toggle_view(self):
        self.view_mode = "grid" if self.view_mode == "list" else "list"
        self.load_game_list(self.search_var.get())

    def change_category(self, value):
        self.current_category = value
        self.load_game_list(self.search_var.get())

    def minimize_to_tray(self):
        self.withdraw()
        
    def restore_from_tray(self):
        self.after(0, self.deiconify)
        
    def quit_app(self):
        self.tray_icon.stop()
        self.controller.stop()
        self.quit()

    def handle_controller_input(self, command):
        # Simple navigation logic
        print(f"Controller: {command}")
        if command == "SELECT":
            # Launch first visible game or focused one (simplified)
            if self.game_cards:
                self.game_cards[0].launch_game()
        # More complex navigation would require tracking focus state

            
    def filter_games(self, *args):
        query = self.search_var.get()
        self.load_game_list(query)

    def add_game_dialog(self):
        file_path = filedialog.askopenfilename(
            title=self.settings_manager.get_text("select_game"),
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        
        if file_path:
            success, message = self.game_manager.add_game(file_path)
            if success:
                self.load_game_list(self.search_var.get())
            else:
                print(message)

    def toggle_favorite(self, path):
        self.game_manager.toggle_favorite(path)
        self.load_game_list(self.search_var.get())

    def open_edit_dialog(self, game_data):
        dialog = EditGameDialog(self, game_data, self.settings_manager, self.save_game_metadata)
        dialog.grab_set() # Modal
        dialog.focus_force()
        
    def save_game_metadata(self, path, name, description, icon_path, categories, launch_args):
        self.game_manager.update_metadata(path, name, description, icon_path, categories, launch_args)
        self.load_game_list(self.search_var.get())
        
        # Update category list in UI
        self.categories = ["All"] + self.game_manager.get_categories()
        self.category_seg.configure(values=self.categories)

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsDialog(self, self.settings_manager, self.refresh_ui)
            self.settings_window.grab_set()
            self.settings_window.focus_force()
        else:
            self.settings_window.focus_force()
            self.settings_window.lift()
            
    def open_music(self):
        if self.music_window is None or not self.music_window.winfo_exists():
            self.music_window = MusicDialog(self, self.music_manager, self.settings_manager)
            self.music_window.grab_set()
            self.music_window.focus_force()
        else:
            self.music_window.focus_force()
            self.music_window.lift()
            
    def spin_wheel(self):
        games = self.game_manager.get_games()
        if not games:
            return
            
        # Visual effect dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.settings_manager.get_text("spin_wheel"))
        dialog.geometry("300x200")
        
        label = ctk.CTkLabel(dialog, text="...", font=("Roboto", 24, "bold"))
        label.pack(expand=True)
        
        def animate(count=0, speed=0.05):
            if count > 20: # Stop after 20 ticks
                winner = random.choice(games)
                label.configure(text=f"{self.settings_manager.get_text('winner')}\n{winner['name']}", text_color="gold")
                return
            
            random_game = random.choice(games)
            label.configure(text=random_game["name"])
            dialog.after(int(speed * 1000), lambda: animate(count + 1, speed * 1.1)) # Slow down
            
        animate()

    def play_startup_video(self, video_path):
        self.withdraw() # Hide main window
        
        video_window = ctk.CTkToplevel(self)
        video_window.title("Startup")
        video_window.attributes("-fullscreen", True)
        video_window.attributes("-topmost", True)
        
        # Label to hold video frame
        label = ctk.CTkLabel(video_window, text="")
        label.pack(fill="both", expand=True)
        
        cap = cv2.VideoCapture(video_path)
        
        def stream():
            ret, frame = cap.read()
            if ret:
                # Resize to fit screen (optional, but good for performance)
                screen_width = video_window.winfo_screenwidth()
                screen_height = video_window.winfo_screenheight()
                frame = cv2.resize(frame, (screen_width, screen_height))
                
                # Convert color
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(screen_width, screen_height))
                
                label.configure(image=ctk_img)
                label.image = ctk_img # Keep reference
                
                video_window.after(33, stream) # ~30 FPS
            else:
                finish()
                
        def finish(event=None):
            cap.release()
            video_window.destroy()
            self.deiconify()
            self.state('zoomed')
            
        video_window.bind("<Button-1>", finish) # Click to skip
        video_window.bind("<Escape>", finish)
        
        stream()

    def toggle_chat(self):
        if not self.username:
            # Ask for username
            user_dialog = ctk.CTkInputDialog(text="Enter Username:", title="Chat Login")
            username = user_dialog.get_input()
            
            if username:
                if self.chat_client.connect(username):
                    self.username = username
                    self.create_friends_panel()
                else:
                    print("Could not connect to broker")
            return

        if self.friends_panel:
            if self.friends_panel.winfo_ismapped():
                self.friends_panel.grid_forget()
            else:
                self.friends_panel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

    def create_friends_panel(self):
        if not self.friends_panel:
            self.friends_panel = FriendsPanel(self, self.chat_client, width=200)
            self.friends_panel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

    def on_chat_message(self, msg):
        # Handle incoming messages from MQTT
        # Must run on main thread
        self.after(0, lambda: self._process_chat_message(msg))
        
    def _process_chat_message(self, msg):
        type = msg.get("type")
        
        if type == "presence":
            # Someone came online or changed status
            username = msg["username"]
            status = msg["status"]
            game = msg["game"]
            
            # If they are in my friends list, update them
            for f in self.friends_panel.friends:
                if f["username"] == username:
                    f["status"] = status
                    f["game"] = game
                    self.friends_panel.refresh_list()
                    
        elif type == "message":
            self.friends_panel.receive_msg(msg["from"], msg["content"])
            
        elif type == "new_request":
            # Add to requests
            if msg["from"] not in self.friends_panel.requests:
                self.friends_panel.requests.append(msg["from"])
                self.friends_panel.req_btn.configure(text=f"Requests ({len(self.friends_panel.requests)})")
                
        elif type == "request_accepted":
            # Add new friend
            friend_name = msg["from"]
            # Check if already exists
            if not any(f["username"] == friend_name for f in self.friends_panel.friends):
                self.friends_panel.friends.append({"username": friend_name, "status": "Online", "game": None})
                self.friends_panel.refresh_list()

    def refresh_ui(self):
        # Update main window texts
        self.title(self.settings_manager.get_text("window_title"))
        self.title_label.configure(text=self.settings_manager.get_text("my_games"))
        self.add_btn.configure(text=self.settings_manager.get_text("add_game"))
        self.scrollable_frame.configure(label_text=self.settings_manager.get_text("library"))
        self.search_entry.configure(placeholder_text=self.settings_manager.get_text("search_placeholder"))
        
        # Update empty label if exists
        if hasattr(self, 'empty_label') and self.empty_label.winfo_exists():
             self.empty_label.configure(text=self.settings_manager.get_text("no_games"))

        # Reload list to update cards
        self.load_game_list(self.search_var.get())

if __name__ == "__main__":
    app = GameLauncherApp()
    app.mainloop()
