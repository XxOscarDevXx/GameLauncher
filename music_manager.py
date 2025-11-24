import pygame
import os
import json

class MusicManager:
    def __init__(self, settings_file="music.json"):
        self.settings_file = settings_file
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_playing = False
        
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

    def load_playlist(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_playlist(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.playlist, f)

    def add_music(self, path):
        if path not in self.playlist and os.path.exists(path):
            self.playlist.append(path)
            self.save_playlist()
            return True
        return False

    def play(self, index=None):
        if not self.playlist:
            return

        if index is not None:
            self.current_index = index
        
        if 0 <= self.current_index < len(self.playlist):
            try:
                pygame.mixer.music.load(self.playlist[self.current_index])
                pygame.mixer.music.play()
                self.is_playing = True
            except Exception as e:
                print(f"Error playing music: {e}")

    def pause(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def get_playlist(self):
        return [os.path.basename(p) for p in self.playlist]
