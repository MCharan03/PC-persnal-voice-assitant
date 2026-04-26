import subprocess
import shutil
import os
from executor.safety import SafetyLayer
from utils.logger import logger

class SystemExecutor:
    def __init__(self):
        # Precise Windows mappings
        self.APPS = {
            "chrome": ["chrome.exe"],
            "vscode": ["Code.exe"],
            "notepad": ["notepad.exe"],
            "browser": ["chrome.exe"],
            "web browser": ["chrome.exe"]
        }

    def execute(self, intent: dict) -> str:
        intent_type = intent.get("type")
        data = intent.get("data", {})

        if intent_type == "OPEN_APP":
            return self.open_app(data.get("app_name"))
        elif intent_type == "CLOSE_APP":
            return self.close_app(data.get("app_name"))
        elif intent_type == "RUN_COMMAND":
            return self.run_command(data.get("command"))
        return "I'm unsure how to perform that action."

    def close_app(self, app_name: str) -> str:
        if not app_name:
            return "Please specify an application to close."
        
        app_name = app_name.lower()
        process_names = self.APPS.get(app_name)
        
        if not process_names:
            return f"I couldn't find {app_name.capitalize()} in my registry."

        success = False
        for proc in process_names:
            try:
                subprocess.run(
                    ["taskkill", "/IM", proc, "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                success = True
            except Exception:
                continue
        
        return f"Closing {app_name.capitalize()}." if success else f"Failed to close {app_name.capitalize()}."

    def open_app(self, app_name: str) -> str:
        if not app_name:
            return "Please specify an application."
        
        app_name = app_name.lower()
        
        # Validation: Check mapping or system path
        targets = self.APPS.get(app_name)
        if not targets:
            if shutil.which(app_name):
                targets = [app_name]
            else:
                return "I couldn't find that application."

        # Execution
        for target in targets:
            try:
                # Resolve full path if it's just a command name
                executable = shutil.which(target) or target
                
                # Launch without shell=True and with NO_WINDOW flag
                subprocess.Popen(
                    [executable],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    start_new_session=True
                )
                return f"Opening {app_name.capitalize()}."
            except Exception as e:
                logger.debug(f"Failed to launch {target}: {e}")
                continue
        
        return f"I failed to launch {app_name.capitalize()}."

    def run_command(self, command: str) -> str:
        if not command:
            return "I need a command to execute."

        if not SafetyLayer.is_safe(command):
            return "That action is blocked for safety."

        try:
            # We use a list to avoid shell=True. 
            # Note: Built-in commands like 'dir' or 'echo' usually require cmd.exe on Windows.
            # To avoid an extra window while still supporting these, we run them via cmd /c silently.
            cmd_args = ["cmd", "/c", command]
            
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                return result.stdout.strip() if result.stdout.strip() else "Done."
            else:
                return "Command failed."
        except Exception as e:
            logger.debug(f"Command execution error: {e}")
            return "I encountered an error running that command."
