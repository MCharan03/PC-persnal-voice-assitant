import numpy as np
from textblob import TextBlob

class EmotionEngine:
    def __init__(self):
        print("Emotion Engine Initialized.")
        # Voice mapping for Kokoro voices (standard set)
        self.voice_map = {
            "EXCITED": {"voice": "af_sky", "speed": 1.2, "tone": "Enthusiastic and fast"},
            "HAPPY": {"voice": "af_bella", "speed": 1.0, "tone": "Cheerful and warm"},
            "ANGRY": {"voice": "am_michael", "speed": 1.1, "tone": "Cold, sharp, and concise"},
            "SAD": {"voice": "af_sarah", "speed": 0.8, "tone": "Soft, slow, and empathetic"},
            "NEUTRAL": {"voice": "af_heart", "speed": 1.0, "tone": "Professional and witty"},
            "CONCERNED": {"voice": "af_sarah", "speed": 0.9, "tone": "Concerned and attentive"}
        }

    def analyze_audio(self, audio_data):
        """
        Analyzes raw audio data for prosodic features.
        Returns a dictionary of features: 'energy', 'zcr' (Zero Crossing Rate).
        """
        if audio_data is None or len(audio_data) == 0:
            return {"energy": 0, "zcr": 0}

        # 1. Energy (RMS) - Volume/Intensity
        energy = np.sqrt(np.mean(audio_data**2))

        # 2. Zero Crossing Rate - Rough proxy for Pitch/Freneticism
        # High ZCR usually means faster speech or higher pitch (or noise)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data))))
        zcr = zero_crossings / len(audio_data)

        return {"energy": energy, "zcr": zcr}

    def analyze(self, text, audio_data=None):
        """
        Analyzes text and optional audio to return a mood state.
        Audio context (loudness, speed) modifies the text sentiment.
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity # -1.0 to 1.0
        
        # Audio Features
        audio_features = self.analyze_audio(audio_data)
        energy = audio_features["energy"]
        zcr = audio_features["zcr"]

        # Thresholds (Tuned for typical normalized float32 audio)
        # Energy > 0.1 is usually loud speaking/shouting
        # ZCR > 0.1 is usually fast/high-pitched
        is_loud = energy > 0.05
        is_quiet = energy < 0.01

        mood = "NEUTRAL"

        # --- FUSION LOGIC ---
        
        if polarity > 0.3:
            if is_loud:
                mood = "EXCITED"
            else:
                mood = "HAPPY"
        
        elif polarity < -0.3:
            if is_loud:
                mood = "ANGRY"
            else:
                mood = "SAD"
        
        else: # Neutral Text
            if is_loud:
                mood = "CONCERNED" # Loud but neutral text = Urgent?
            elif is_quiet:
                mood = "SAD" # Quiet + Neutral often reads als somber
            else:
                mood = "NEUTRAL"

        print(f">> Emotion Analysis: Text={polarity:.2f}, Energy={energy:.2f} -> {mood}")
        return mood

    def get_voice_settings(self, mood):
        return self.voice_map.get(mood, self.voice_map["NEUTRAL"])

    def get_system_directive(self, mood):
        """
        Returns a prompt injection based on the user's mood.
        """
        settings = self.get_voice_settings(mood)
        tone = settings["tone"]
        
        directives = {
            "EXCITED": f"The user is excited (High Energy)! {tone}. Match their high energy.",
            "HAPPY": f"The user is in a good mood. {tone}.",
            "ANGRY": f"The user sounds angry/annoyed (High Energy). {tone}. Be efficient. Do not joke.",
            "SAD": f"The user seems down or quiet. {tone}. Be comforting.",
            "CONCERNED": f"The user sounds urgent or concerned. {tone}. Focus on the task.",
            "NEUTRAL": f"The user is neutral. {tone} (Standard Jarvis Mode)."
        }
        return directives.get(mood, directives["NEUTRAL"])

if __name__ == "__main__":
    e = EmotionEngine()
    print(e.analyze("I hate this.", audio_data=np.random.normal(0, 0.1, 1000))) # Simulated Loud
    print(e.analyze("I hate this.", audio_data=np.random.normal(0, 0.001, 1000))) # Simulated Quiet
