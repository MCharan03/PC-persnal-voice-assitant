import threading
import time
import os
import cv2
import numpy as np
from PIL import ImageGrab
import ollama
from modules.memory_vector import MemoryVector
from config import settings

class VisualBuffer(threading.Thread):
    def __init__(self, interval=60):
        super().__init__(daemon=True)
        self.interval = interval
        self.running = True
        self.memory_vector = MemoryVector()
        print(f"Visual Buffer (Passive Awareness) initialized. Interval: {interval}s")

    def run(self):
        while self.running:
            try:
                # 1. Capture Screen
                screenshot = ImageGrab.grab()
                
                # 2. Resize to save processing time (optional but recommended for Llava)
                screenshot.thumbnail((640, 480))
                
                # 3. Convert to bytes for Ollama
                import io
                img_byte_arr = io.BytesIO()
                screenshot.save(img_byte_arr, format='JPEG', quality=70)
                image_data = img_byte_arr.getvalue()
                
                # 4. Describe with Vision Model (Quietly)
                # We use a very short prompt to keep it fast
                response = ollama.chat(
                    model='llava:7b', # Or a smaller vision model if available
                    messages=[{
                        'role': 'user', 
                        'content': "Describe in ONE short sentence what the user is doing on this screen.", 
                        'images': [image_data]
                    }]
                )
                
                description = response['message']['content'].strip()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 5. Store in Memory Vector
                visual_fact = f"At {timestamp}, I saw: {description}"
                print(f">> [Passive Awareness] {visual_fact}")
                self.memory_vector.remember_fact(visual_fact)
                
            except Exception as e:
                print(f"Visual Buffer Error: {e}")
            
            time.sleep(self.interval)

    def stop(self):
        self.running = False

visual_buffer = VisualBuffer(interval=120) # 2 minutes for performance
