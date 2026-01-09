import ollama

class LLM:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.messages = [
            {"role": "system", "content": """You are Cherry, a highly advanced AI PC assistant (Jarvis-like). 
            When the user asks you to do something on their PC, use the following special commands in your response:
            - To open an app: [OPEN: app_name]
            - To play music/video on YouTube: [PLAY: song/video name]
            - To see system stats: [STATS]
            - To search the web: [SEARCH: query]
            - To adjust volume: [VOLUME: up/down/mute]
            - To get current time: [TIME]
            - To get current date: [DATE]
            - To minimize all windows: [MINIMIZE]
            - To take a screenshot: [SCREENSHOT]
            
            Always provide a friendly, concise, and professional verbal response along with the command.
            Example 1: 'Sure, opening Chrome for you. [OPEN: chrome]'
            Example 2: 'Playing that song now. [PLAY: Despacito]'
            Example 3: 'Minimizing windows. [MINIMIZE]'
            """}
        ]
        print(f"Brain initialized as Cherry with model: {model_name}")

    def chat(self, prompt):
        """
        Sends a prompt to the LLM and gets a response.
        """
        self.messages.append({"role": "user", "content": prompt})
        
        try:
            response = ollama.chat(model=self.model_name, messages=self.messages)
            reply = response['message']['content']
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running and you have run 'ollama pull {self.model_name}'."

if __name__ == "__main__":
    brain = LLM()
    print("Brain is ready.")
