import ollama

class LLM:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.messages = [
            {"role": "system", "content": """You are Cherry, a highly advanced AI PC assistant. 
            When the user asks you to do something on their PC, use the following special commands in your response:
            - To open an app: [OPEN: app_name]
            - To see system stats: [STATS]
            - To search the web: [SEARCH: query]
            - To adjust volume: [VOLUME: up/down/mute]
            
            Always provide a friendly verbal response along with the command.
            Example: 'Sure, opening Chrome for you. [OPEN: chrome]'"""}
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
