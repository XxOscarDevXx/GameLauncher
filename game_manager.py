import json
import os
import time
from icon_extractor import extract_icon

class GameManager:
    def __init__(self, data_file="games.json", icons_dir="icons"):
        self.data_file = data_file
        self.icons_dir = icons_dir
        self.games = self.load_games()
        
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir)

    def load_games(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    games = json.load(f)
                    # Ensure all fields exist for backward compatibility
                    for game in games:
                        game.setdefault("favorite", False)
                        game.setdefault("play_time", 0)
                        game.setdefault("description", "")
                        game.setdefault("last_played", None)
                    return games
            except json.JSONDecodeError:
                return []
        return []

    def save_games(self):
        with open(self.data_file, "w") as f:
            json.dump(self.games, f, indent=4)

    def add_game(self, file_path):
        if not os.path.exists(file_path):
            return False, "File does not exist."

        name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Check if game already exists
        for game in self.games:
            if game["path"] == file_path:
                return False, "Game already added."

        icon_filename = f"{name}.png"
        icon_path = os.path.join(self.icons_dir, icon_filename)
        
        # Extract icon
        extracted_path = extract_icon(file_path, icon_path)
        if not extracted_path:
             print(f"Warning: Could not extract icon for {name}")
             icon_path = None

        game_data = {
            "name": name,
            "path": file_path,
            "icon": icon_path,
            "favorite": False,
            "play_time": 0,
            "description": "",
            "last_played": None
        }
        
        self.games.append(game_data)
        self.save_games()
        return True, "Game added successfully."

    def get_games(self):
        # Sort: Favorites first, then alphabetical
        return sorted(self.games, key=lambda x: (not x.get("favorite", False), x["name"].lower()))

    def remove_game(self, index):
        if 0 <= index < len(self.games):
            self.games.pop(index)
            self.save_games()
            return True
        return False

    def toggle_favorite(self, path):
        for game in self.games:
            if game["path"] == path:
                game["favorite"] = not game.get("favorite", False)
                self.save_games()
                return True
        return False

    def update_play_time(self, path, duration_seconds):
        for game in self.games:
            if game["path"] == path:
                current_time = game.get("play_time", 0)
                game["play_time"] = current_time + duration_seconds
                game["last_played"] = time.time()
                self.save_games()
                return True
        return False

    def update_metadata(self, path, name, description, icon_path=None):
        for game in self.games:
            if game["path"] == path:
                game["name"] = name
                game["description"] = description
                if icon_path:
                    game["icon"] = icon_path
                self.save_games()
                return True
        return False
