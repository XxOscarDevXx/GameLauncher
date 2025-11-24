import pygame
import os

class SoundManager:
    def __init__(self, sounds_dir="sounds"):
        self.sounds_dir = sounds_dir
        self.sounds = {}
        self.enabled = True
        
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)
            
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.load_sounds()

    def load_sounds(self):
        sound_files = {
            "hover": "hover.wav",
            "click": "click.wav",
            "launch": "launch.wav",
            "back": "back.wav"
        }
        
        for name, filename in sound_files.items():
            path = os.path.join(self.sounds_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.3) # Default volume
                except Exception as e:
                    print(f"Error loading sound {name}: {e}")

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def set_volume(self, volume):
        # volume 0.0 to 1.0
        for sound in self.sounds.values():
            sound.set_volume(volume)
