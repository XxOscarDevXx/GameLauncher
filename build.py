import PyInstaller.__main__
import customtkinter
import os
import sys

# Get the path to customtkinter to include its data files
ctk_path = os.path.dirname(customtkinter.__file__)

# Define arguments for PyInstaller
args = [
    'app.py',  # Main script
    '--name=GameLauncher',  # Name of the executable
    '--noconsole',  # Hide the console window
    '--onefile',  # Bundle everything into a single exe (optional, remove for directory based)
    '--clean',  # Clean cache
    
    # Add CustomTkinter data (themes, etc.)
    f'--add-data={ctk_path};customtkinter',
    
    # Add our local icons folder
    '--add-data=icons;icons',
    
    # Hidden imports that might be missed
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=win32timezone',
    
    # Icon for the exe itself (if you have one, otherwise comment out)
    # '--icon=icons/app_icon.ico', 
]

print("Building Game Launcher EXE...")
PyInstaller.__main__.run(args)
print("Build complete! Check the 'dist' folder.")
