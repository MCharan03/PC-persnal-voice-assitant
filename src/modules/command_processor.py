import re
from modules.actions import Actions

class CommandProcessor:
    def __init__(self, actions_module=None):
        self.actions = actions_module if actions_module else Actions()

    def process(self, text):
        """
        Parses the text for commands like [OPEN:...] and executes them.
        Returns the clean text to be spoken/displayed.
        """
        response = text

        # Replacement commands (They add text to the response)
        if "[STATS]" in response:
            stats = self.actions.get_system_stats()
            response = response.replace("[STATS]", "") + f" {stats}"
        
        if "[TIME]" in response:
            time_str = self.actions.get_time()
            response = response.replace("[TIME]", "") + f" {time_str}"
            
        if "[DATE]" in response:
            date_str = self.actions.get_date()
            response = response.replace("[DATE]", "") + f" {date_str}"
            
        if "[SCREENSHOT]" in response:
            result = self.actions.take_screenshot()
            response = response.replace("[SCREENSHOT]", "") + f" {result}"

        # Action commands (They execute side effects and are removed from text)
        
        if "[MINIMIZE]" in response:
            self.actions.minimize_all()
            response = response.replace("[MINIMIZE]", "")

        # Regex based commands
        # We iterate to find matches
        
        # OPEN
        match = re.search(r"\[OPEN:\s*(.*?)\]", response)
        if match:
            self.actions.open_app(match.group(1))
            response = response.replace(match.group(0), "")

        # SEARCH
        match = re.search(r"\[SEARCH:\s*(.*?)\]", response)
        if match:
            self.actions.search_web(match.group(1))
            response = response.replace(match.group(0), "")

        # PLAY
        match = re.search(r"\[PLAY:\s*(.*?)\]", response)
        if match:
            self.actions.play_youtube(match.group(1))
            response = response.replace(match.group(0), "")

        # VOLUME
        match = re.search(r"\[VOLUME:\s*(.*?)\]", response)
        if match:
            self.actions.adjust_volume(match.group(1))
            response = response.replace(match.group(0), "")

        # MEDIA
        match = re.search(r"\[MEDIA:\s*(.*?)\]", response)
        if match:
            self.actions.control_media(match.group(1))
            response = response.replace(match.group(0), "")

        return response.strip()
