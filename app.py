import customtkinter as ctk
from tkinter import filedialog, Menu
from PIL import Image
import os
import subprocess
import threading
import time
from game_manager import GameManager
from settings_manager import SettingsManager
from metadata_fetcher import fetch_metadata

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
            # Note: Handling image URL download is skipped for simplicity, 
            # but could be added here.
            
    def save(self):
        new_name = self.name_entry.get()
        new_desc = self.desc_textbox.get("0.0", "end").strip()
        self.save_callback(self.game_data["path"], new_name, new_desc, self.icon_path)
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
        self.configure(fg_color=("gray85", "gray17"))
        self.pack(pady=5, padx=10, fill="x", expand=True)
        
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
        self.play_btn = ctk.CTkButton(self.btn_frame, text=self.settings_manager.get_text("play"), command=self.launch_game, width=80)
        self.play_btn.pack(side="left")

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

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings_manager, refresh_callback):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.refresh_callback = refresh_callback
        self.title(settings_manager.get_text("settings"))
        self.geometry("300x300")
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
        
    def change_language(self, choice):
        lang_code = "en" if choice == "English" else "es"
        self.settings_manager.set_setting("language", lang_code)
        self.refresh_callback()
        self.title(self.settings_manager.get_text("settings"))
        
    def change_theme(self, theme_code):
        self.settings_manager.set_setting("theme", theme_code)
        ctk.set_default_color_theme(theme_code)
        # Note: Theme change usually requires restart or complex reload, 
        # but we can try to notify user or just save it.
        # For immediate effect on some widgets, we might need to recreate them,
        # but ctk.set_default_color_theme mainly affects new widgets.
        # We will rely on restart for full effect or simple re-render.
        self.refresh_callback()

class GameLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.game_manager = GameManager()
        self.settings_manager = SettingsManager()
        
        # Apply saved theme
        saved_theme = self.settings_manager.get_setting("theme", "dark-blue")
        ctk.set_default_color_theme(saved_theme)
        
        self.title(self.settings_manager.get_text("window_title"))
        self.geometry("500x700")
        
        self.settings_window = None

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text=self.settings_manager.get_text("my_games"), font=("Roboto", 20, "bold"))
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_games)
        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text=self.settings_manager.get_text("search_placeholder"), textvariable=self.search_var, width=150)
        self.search_entry.pack(side="left", padx=20, pady=15)
        
        # Settings Button
        settings_icon_path = os.path.join("icons", "settings.png")
        self.settings_image = None
        if os.path.exists(settings_icon_path):
             try:
                pil_image = Image.open(settings_icon_path)
                self.settings_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(20, 20))
             except:
                 pass

        self.settings_btn = ctk.CTkButton(
            self.header_frame, 
            text="" if self.settings_image else "⚙️", 
            image=self.settings_image,
            width=30, 
            command=self.open_settings,
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        self.settings_btn.pack(side="right", padx=(5, 20), pady=15)

        self.add_btn = ctk.CTkButton(self.header_frame, text=self.settings_manager.get_text("add_game"), command=self.add_game_dialog, width=100)
        self.add_btn.pack(side="right", padx=5, pady=15)
        
        # Game List
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text=self.settings_manager.get_text("library"))
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.game_cards = []
        self.load_game_list()

    def load_game_list(self, query=""):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.game_cards = []
            
        games = self.game_manager.get_games()
        
        # Filter
        if query:
            games = [g for g in games if query.lower() in g["name"].lower()]
        
        if not games:
            self.empty_label = ctk.CTkLabel(self.scrollable_frame, text=self.settings_manager.get_text("no_games"), text_color="gray50")
            self.empty_label.pack(pady=50)
            return

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

    def launch_game(self, path):
        if os.path.exists(path):
            # Run in thread to track time without blocking UI
            threading.Thread(target=self._run_game_process, args=(path,), daemon=True).start()
        else:
            print(self.settings_manager.get_text("game_not_found"))
            
    def _run_game_process(self, path):
        try:
            start_time = time.time()
            process = subprocess.Popen([path], cwd=os.path.dirname(path))
            process.wait() # Wait for game to close
            end_time = time.time()
            
            duration = end_time - start_time
            self.game_manager.update_play_time(path, duration)
            
            # Update UI (schedule on main thread ideally, but simple refresh works)
            self.after(100, lambda: self.load_game_list(self.search_var.get()))
            
        except Exception as e:
            print(f"{self.settings_manager.get_text('error_launch')}: {e}")

    def toggle_favorite(self, path):
        self.game_manager.toggle_favorite(path)
        self.load_game_list(self.search_var.get())

    def open_edit_dialog(self, game_data):
        EditGameDialog(self, game_data, self.settings_manager, self.save_game_metadata)
        
    def save_game_metadata(self, path, name, description, icon_path):
        self.game_manager.update_metadata(path, name, description, icon_path)
        self.load_game_list(self.search_var.get())

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsDialog(self, self.settings_manager, self.refresh_ui)
        else:
            self.settings_window.focus()

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
