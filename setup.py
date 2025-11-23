import sys
import os
from cx_Freeze import setup, Executable
import customtkinter

# Get the path to customtkinter to include its data files
ctk_path = os.path.dirname(customtkinter.__file__)

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "customtkinter", "PIL", "threading", "time", "subprocess", "json", "urllib"],
    "include_files": [
        (ctk_path, "customtkinter"),
        ("icons", "icons")
    ],
    "excludes": []
}

# MSI Options
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "Game Launcher",          # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]GameLauncher.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),
    ("ProgramMenuShortcut",    # Shortcut
     "ProgramMenuFolder",      # Directory_
     "Game Launcher",          # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]GameLauncher.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
]

msi_data = {"Shortcut": shortcut_table}

bdist_msi_options = {
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\GameLauncher",
    "upgrade_code": "{96a85b22-9f4c-45db-9a8e-4e389a4b8f2c}", # Unique ID for this app
    "data": msi_data
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="GameLauncher",
    version="1.1", # Bump version to force upgrade behavior if needed
    description="Elegant Game Launcher",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[Executable("app.py", base=base, target_name="GameLauncher.exe", icon="icons/settings.png")]
)
