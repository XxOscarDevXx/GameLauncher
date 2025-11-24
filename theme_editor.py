import customtkinter as ctk
import json
import os
from tkinter import colorchooser

class ThemeEditorDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings_manager, apply_callback):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.apply_callback = apply_callback
        self.title(self.settings_manager.get_text("theme_editor"))
        self.geometry("400x500")
        
        self.colors = {
            "primary": "#1f538d",
            "hover": "#14375e",
            "text": "#ffffff"
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Primary Color
        ctk.CTkLabel(self, text=self.settings_manager.get_text("primary_color")).grid(row=0, column=0, padx=20, pady=20)
        self.primary_btn = ctk.CTkButton(self, text="", width=50, height=25, fg_color=self.colors["primary"], command=lambda: self.pick_color("primary"))
        self.primary_btn.grid(row=0, column=1, padx=20, pady=20)
        
        # Hover Color
        ctk.CTkLabel(self, text=self.settings_manager.get_text("hover_color")).grid(row=1, column=0, padx=20, pady=20)
        self.hover_btn = ctk.CTkButton(self, text="", width=50, height=25, fg_color=self.colors["hover"], command=lambda: self.pick_color("hover"))
        self.hover_btn.grid(row=1, column=1, padx=20, pady=20)
        
        # Text Color
        ctk.CTkLabel(self, text=self.settings_manager.get_text("text_color")).grid(row=2, column=0, padx=20, pady=20)
        self.text_btn = ctk.CTkButton(self, text="", width=50, height=25, fg_color=self.colors["text"], command=lambda: self.pick_color("text"))
        self.text_btn.grid(row=2, column=1, padx=20, pady=20)
        
        # Apply Button
        ctk.CTkButton(self, text=self.settings_manager.get_text("apply"), command=self.save_theme).grid(row=3, column=0, columnspan=2, pady=40)
        
    def pick_color(self, key):
        color = colorchooser.askcolor(color=self.colors[key])[1]
        if color:
            self.colors[key] = color
            if key == "primary":
                self.primary_btn.configure(fg_color=color)
            elif key == "hover":
                self.hover_btn.configure(fg_color=color)
            elif key == "text":
                self.text_btn.configure(fg_color=color)
                
    def save_theme(self):
        theme_data = {
            "CTk": {
                "fg_color": ["gray92", "gray14"],
            },
            "CTkButton": {
                "fg_color": [self.colors["primary"], self.colors["primary"]],
                "hover_color": [self.colors["hover"], self.colors["hover"]],
                "text_color": [self.colors["text"], self.colors["text"]]
            },
             "CTkEntry": {
                "fg_color": ["gray92", "gray14"],
             },
             "CTkLabel": {
                 "text_color": [self.colors["text"], self.colors["text"]]
             }
             # Add more widgets as needed for a full theme
        }
        
        # For now, we just apply these colors to the current app instance manually or create a temporary theme file
        # Creating a full theme json is complex, so we'll just save a custom.json
        
        if not os.path.exists("themes"):
            os.makedirs("themes")
            
        # We need a base theme to copy from, but for now let's just create a simple one
        # Actually, customtkinter expects a specific structure. 
        # To keep it simple, we will just update the default color theme if possible or save a minimal json
        
        # Let's try to load the blue.json and modify it
        base_theme_path = os.path.join(os.path.dirname(ctk.__file__), "assets", "themes", "blue.json")
        try:
            with open(base_theme_path, "r") as f:
                base_theme = json.load(f)
                
            base_theme["CTkButton"]["fg_color"] = [self.colors["primary"], self.colors["primary"]]
            base_theme["CTkButton"]["hover_color"] = [self.colors["hover"], self.colors["hover"]]
            
            custom_theme_path = os.path.join("themes", "custom.json")
            with open(custom_theme_path, "w") as f:
                json.dump(base_theme, f, indent=4)
                
            self.apply_callback("custom")
            self.destroy()
            
        except Exception as e:
            print(f"Error creating theme: {e}")
