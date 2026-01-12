from textblob import TextBlob

class EmotionEngine:
    def __init__(self):
        print("Emotion Engine Initialized.")

    def analyze(self, text):
        """
        Analyzes text and returns a mood state and confidence.
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity # -1.0 to 1.0
        
        # Simple classification
        if polarity > 0.5:
            return "EXCITED"
        elif polarity > 0.1:
            return "HAPPY"
        elif polarity < -0.5:
            return "ANGRY"
        elif polarity < -0.1:
            return "SAD"
        else:
            return "NEUTRAL"

    def get_system_directive(self, mood):
        """
        Returns a prompt injection based on the user's mood.
        """
        directives = {
            "EXCITED": "The user is excited! Match their energy. Be enthusiastic and quick.",
            "HAPPY": "The user is in a good mood. Be cheerful and helpful.",
            "ANGRY": "The user sounds annoyed. Be extremely concise, apologetic, and solution-oriented. Do not joke.",
            "SAD": "The user seems down. Be empathetic, soft-spoken, and supportive.",
            "NEUTRAL": "The user is neutral. Be professional, witty, and efficient (Standard Jarvis Mode)."
        }
        return directives.get(mood, directives["NEUTRAL"])

if __name__ == "__main__":
    e = EmotionEngine()
    print(e.analyze("I hate this bug!"))
    print(e.analyze("I just got promoted!"))
