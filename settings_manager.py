import json
import os

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
        
        self.translations = {
            "en": {
                "window_title": "Game Launcher",
                "my_games": "My Games",
                "add_game": "+ Add Game",
                "library": "Library",
                "play": "Play",
                "settings": "Settings",
                "language": "Language",
                "no_games": "No games added yet.\nClick '+ Add Game' to start.",
                "select_game": "Select Game Executable",
                "game_added": "Game added successfully.",
                "file_not_exist": "File does not exist.",
                "game_exists": "Game already added.",
                "error_launch": "Error launching game",
                "game_not_found": "Game file not found!",
                "english": "English",
                "spanish": "Spanish",
                "search_placeholder": "Search games...",
                "favorites": "Favorites",
                "time_played": "Time Played",
                "hours": "h",
                "minutes": "m",
                "edit": "Edit",
                "save": "Save",
                "cancel": "Cancel",
                "description": "Description",
                "fetch_metadata": "Fetch Data",
                "theme": "Theme",
                "blue": "Blue",
                "green": "Green",
                "dark_blue": "Dark Blue",
                "music_player": "Music Player",
                "add_music": "Add Music",
                "no_music": "No music added",
                "spin_wheel": "Spin the Wheel",
                "winner": "Winner!",
                "categories": "Categories",
                "all": "All",
                "grid_view": "Grid View",
                "list_view": "List View",
                "theme_editor": "Theme Editor",
                "open": "Open",
                "quit": "Quit",
                "primary_color": "Primary Color",
                "hover_color": "Hover Color",
                "text_color": "Text Color",
                "apply": "Apply",
                "startup_video": "Startup Video",
                "select_video": "Select Video",
                "remove_video": "Remove Video",
                "launch_args": "Launch Arguments"
            },
            "es": {
                "window_title": "Lanzador de Juegos",
                "my_games": "Mis Juegos",
                "add_game": "+ Añadir Juego",
                "library": "Biblioteca",
                "play": "Jugar",
                "settings": "Ajustes",
                "language": "Idioma",
                "no_games": "No hay juegos añadidos.\nHaz clic en '+ Añadir Juego' para empezar.",
                "select_game": "Seleccionar Ejecutable del Juego",
                "game_added": "Juego añadido con éxito.",
                "file_not_exist": "El archivo no existe.",
                "game_exists": "El juego ya está añadido.",
                "error_launch": "Error al lanzar el juego",
                "game_not_found": "¡Archivo del juego no encontrado!",
                "english": "Inglés",
                "spanish": "Español",
                "search_placeholder": "Buscar juegos...",
                "favorites": "Favoritos",
                "time_played": "Tiempo Jugado",
                "hours": "h",
                "minutes": "m",
                "edit": "Editar",
                "save": "Guardar",
                "cancel": "Cancelar",
                "description": "Descripción",
                "fetch_metadata": "Obtener Datos",
                "theme": "Tema",
                "blue": "Azul",
                "green": "Verde",
                "dark_blue": "Azul Oscuro",
                "music_player": "Reproductor de Música",
                "add_music": "Añadir Música",
                "no_music": "Sin música añadida",
                "spin_wheel": "Girar la Rueda",
                "winner": "¡Ganador!",
                "categories": "Categorías",
                "all": "Todos",
                "grid_view": "Vista Cuadrícula",
                "list_view": "Vista Lista",
                "theme_editor": "Editor de Temas",
                "open": "Abrir",
                "quit": "Salir",
                "primary_color": "Color Primario",
                "hover_color": "Color al Pasar",
                "text_color": "Color de Texto",
                "apply": "Aplicar",
                "startup_video": "Video de Inicio",
                "select_video": "Seleccionar Video",
                "remove_video": "Eliminar Video",
                "launch_args": "Argumentos de Lanzamiento"
            }
        }

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"language": "en"}
        return {"language": "en"}

    def save_settings(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_text(self, key):
        lang = self.settings.get("language", "en")
        return self.translations.get(lang, self.translations["en"]).get(key, key)
