import os
import winshell

def remove_startup_shortcut():
    startup_folder = winshell.startup()
    path = os.path.join(startup_folder, "CherryAssistant.lnk")
    
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"Startup shortcut removed from: {path}")
            print("Cherry will no longer start automatically.")
        except Exception as e:
            print(f"Error removing shortcut: {e}")
    else:
        print(f"Startup shortcut not found at: {path}")

if __name__ == "__main__":
    remove_startup_shortcut()
