import os
import sys
import winshell
from win32com.client import Dispatch

def create_startup_shortcut():
    startup_folder = winshell.startup()
    path = os.path.join(startup_folder, "CherryAssistant.lnk")
    
    # Path to pythonw.exe (Windowless Python)
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    
    # Path to boot script
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "boot.py"))
    
    # Working Directory
    work_dir = os.path.dirname(script) # src/
    project_root = os.path.dirname(work_dir) # root
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.TargetPath = python_exe
    shortcut.Arguments = f'"{script}"'
    shortcut.WorkingDirectory = project_root
    shortcut.IconLocation = python_exe
    shortcut.Description = "Starts Cherry Voice Assistant Background Service"
    shortcut.save()
    
    print(f"Startup shortcut created at: {path}")
    print("Cherry will now start automatically when you log in.")

if __name__ == "__main__":
    create_startup_shortcut()
