import re

class Normalizer:
    # Sorted by length descending to ensure longest matches are replaced first
    MAPPINGS = [
        ("visual studio code", "vscode"),
        ("visual studio", "vscode"),
        ("visual code", "vscode"),
        ("vs code", "vscode"),
        ("vs", "vscode"),
        ("system 32", "system32"),
        ("note pad", "notepad"),
        ("chrome browser", "chrome"),
        ("google chrome", "chrome"),
        ("web browser", "chrome")
    ]

    @staticmethod
    def normalize(text: str) -> str:
        """Normalizes input text with longest-match priority."""
        if not text:
            return ""
        
        text = text.lower().strip()
        
        # Apply mappings in order
        for variation, correct in Normalizer.MAPPINGS:
            text = re.sub(rf'\b{variation}\b', correct, text)
            
        return re.sub(r'\s+', ' ', text).strip()
