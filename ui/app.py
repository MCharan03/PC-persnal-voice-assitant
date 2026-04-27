import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import sys
import os

# Add the project root to sys.path so modules can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.brain import Brain
from core.intent import IntentParser
from core.decision import DecisionEngine
from core.planner import Planner
from executor.system import SystemExecutor
from executor.safety import SafetyLayer
from memory.storage import Memory
from utils.config_loader import config
from utils.normalizer import Normalizer
from utils.state import StateTracker, State

class SambaUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SAMBA Assistant")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e")

        # Initialize Backend
        self.memory = Memory()
        self.executor = SystemExecutor()
        self.intent_parser = IntentParser(memory=self.memory)
        self.brain = Brain()
        self.decision_engine = DecisionEngine(memory=self.memory)
        self.planner = Planner(memory=self.memory)

        # UI Components
        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header = tk.Label(
            self.root, text="SAMBA ASSISTANT", 
            bg="#1e1e1e", fg="#00ff00", 
            font=("Courier", 16, "bold"), pady=10
        )
        self.header.pack()

        # Status Label
        self.status_var = tk.StringVar(value="IDLE")
        self.status_label = tk.Label(
            self.root, textvariable=self.status_var,
            bg="#1e1e1e", fg="#ffff00",
            font=("Courier", 10)
        )
        self.status_label.pack()

        # Output Area
        self.output_area = scrolledtext.ScrolledText(
            self.root, bg="#000000", fg="#00ff00",
            insertbackground="white", font=("Courier", 10),
            padx=10, pady=10, state='disabled'
        )
        self.output_area.pack(expand=True, fill='both', padx=20, pady=10)

        # Input Frame
        self.input_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.input_frame.pack(fill='x', padx=20, pady=10)

        self.input_box = tk.Entry(
            self.input_frame, bg="#333333", fg="white",
            insertbackground="white", font=("Courier", 12),
            borderwidth=0, highlightthickness=1, highlightbackground="#444444"
        )
        self.input_box.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.input_box.bind("<Return>", lambda e: self.process_command())

        self.run_btn = tk.Button(
            self.input_frame, text="RUN",
            bg="#00ff00", fg="black",
            font=("Courier", 10, "bold"),
            command=self.process_command,
            borderwidth=0, padx=15
        )
        self.run_btn.pack(side='right')

        self._log("SAMBA: System status: Online. Ready for commands.")

    def _log(self, text):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state='disabled')

    def set_status(self, status_text):
        self.status_var.set(status_text)
        if status_text == "THINKING":
            self.status_label.configure(fg="#ffff00")
        elif status_text == "EXECUTING":
            self.status_label.configure(fg="#ff00ff")
        else:
            self.status_label.configure(fg="#00ff00")
        self.root.update_idletasks()

    def process_command(self):
        user_input = self.input_box.get().strip()
        if not user_input:
            return

        self.input_box.delete(0, tk.END)
        self._log(f"You: {user_input}")
        
        # Run in thread to prevent UI freeze
        threading.Thread(target=self._backend_thread, args=(user_input,), daemon=True).start()

    def _backend_thread(self, user_input):
        try:
            # 1. THINK Phase
            self.set_status("THINKING")
            raw_input = Normalizer.normalize(user_input)

            if SafetyLayer.is_dangerous(raw_input):
                self._log("SAMBA: That action is blocked for safety.")
                self.set_status("IDLE")
                return

            intent = self.intent_parser.detect_intent(raw_input)
            context = self.memory.get_recent_context(n=3)
            decision = self.decision_engine.decide(raw_input, intent, context)

            # 2. PLAN & EXECUTE Phase
            self.set_status("EXECUTING")
            
            if decision["action"] in ["EXECUTE", "MULTI"]:
                plan = self.planner.create_plan(raw_input, intent)
                if not plan:
                    self._log("SAMBA: I couldn't formulate a plan for that.")
                else:
                    for step in plan:
                        if SafetyLayer.is_dangerous(step):
                            self._log(f"SAMBA: Blocked dangerous part: {step}")
                            continue
                        
                        step_intent = self.intent_parser.detect_intent(step)
                        res = self.executor.execute(step_intent)
                        self._log(f"SAMBA: {res}")
                        self.memory.add_interaction(step, res, step_intent["type"])
            
            elif decision["action"] == "CHAT":
                full_context = self.memory.get_context()
                response = self.brain.think(raw_input, full_context)
                self._log(f"SAMBA: {response}")
                self.memory.add_interaction(raw_input, response, "CHAT")

            elif decision["action"] == "ASK":
                self._log("SAMBA: I'm not quite sure what you mean. Could you rephrase that?")

        except Exception as e:
            self._log(f"SAMBA: System Error: {str(e)}")
        
        self.set_status("IDLE")

if __name__ == "__main__":
    root = tk.Tk()
    app = SambaUI(root)
    root.mainloop()
