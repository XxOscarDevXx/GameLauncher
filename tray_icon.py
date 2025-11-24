import pystray
from PIL import Image
import threading
import os

class TrayIcon:
    def __init__(self, icon_path, show_callback, quit_callback):
        self.icon_path = icon_path
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.icon = None
        self.thread = None

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Open", self.on_show),
            pystray.MenuItem("Quit", self.on_quit)
        )

    def on_show(self, icon, item):
        self.show_callback()

    def on_quit(self, icon, item):
        self.quit_callback()

    def run(self):
        if not os.path.exists(self.icon_path):
            print("Tray icon not found")
            return

        image = Image.open(self.icon_path)
        self.icon = pystray.Icon("GameLauncher", image, "Game Launcher", self.create_menu())
        self.icon.run()

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()
