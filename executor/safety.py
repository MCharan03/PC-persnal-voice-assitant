class SafetyLayer:
    BLOCKLIST = [
        "rm -rf", "delete system32", "format ", "shutdown", 
        "del /f", "erase ", "mkfs", "dd ", "chmod 777",
        ":(){ :|:& };:"
    ]

    @staticmethod
    def is_safe(command: str) -> bool:
        """Checks if a command contains any blacklisted strings."""
        cmd_lower = command.lower().strip()
        for forbidden in SafetyLayer.BLOCKLIST:
            if forbidden in cmd_lower:
                return False
        return True

    @staticmethod
    def is_dangerous(user_input: str) -> bool:
        """Early check for dangerous user input patterns."""
        user_input_lower = user_input.lower().strip()
        for forbidden in SafetyLayer.BLOCKLIST:
            if forbidden in user_input_lower:
                return True
        return False
