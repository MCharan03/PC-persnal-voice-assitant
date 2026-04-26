import json
import time
import re
from core.brain import Brain
from core.intent import IntentParser
from core.decision import DecisionEngine
from core.planner import Planner
from executor.system import SystemExecutor
from executor.safety import SafetyLayer
from memory.storage import Memory
from utils.config_loader import config
from utils.logger import logger
from utils.state import StateTracker, State

def clean_text(text):
    """Removes special/unicode characters and returns clean string."""
    if not text: return ""
    return re.sub(r'[^\x00-\x7F]+', '', str(text)).strip()

from voice.input import VoiceInput
from voice.output import VoiceOutput

from utils.normalizer import Normalizer

def main():
    print(f"--- {config.get('assistant_name', 'SAMBA')} Online ---")
    
    # Mode Selection
    print("\n1 = Text Mode\n2 = Voice Mode")
    mode = input("Select Mode: ").strip()
    use_voice = mode == "2"

    memory = Memory()
    executor = SystemExecutor()
    intent_parser = IntentParser(memory=memory)
    brain = Brain()
    decision_engine = DecisionEngine(memory=memory)
    planner = Planner(memory=memory)
    
    v_input = VoiceInput() if use_voice else None
    v_output = VoiceOutput() if use_voice else None

    if use_voice:
        print("SAMBA: Voice mode active. Listening...")

    while True:
        try:
            StateTracker.set_state(State.IDLE)
            time.sleep(0.5) # Prevent rapid accidental triggers
            
            if use_voice:
                raw_input = v_input.listen()
                if not raw_input: continue
            else:
                user_input_raw = input("\nYou: ").strip()
                if not user_input_raw: continue
                # 1. NORMALIZE FIRST
                raw_input = Normalizer.normalize(user_input_raw)
            
            if raw_input.lower() in ["exit", "quit", "goodbye"]:
                msg = "Goodbye, sir."
                print(f"SAMBA: {msg}")
                if v_output: v_output.speak(msg)
                break

            # 1. THINK Phase
            StateTracker.set_state(State.THINKING)
            
            # 2. SAFETY CHECK (on normalized input)
            if SafetyLayer.is_dangerous(raw_input):
                msg = "That action is blocked for safety."
                print(f"SAMBA: {msg}")
                if v_output: v_output.speak(msg)
                continue

            # 3. INTENT DETECTION
            logger.start_timer("intent")
            intent = intent_parser.detect_intent(raw_input)
            logger.end_timer("intent")
            
            # Validation for unclear/partial commands
            if intent["type"] in ["OPEN_APP", "RUN_COMMAND", "CLOSE_APP"]:
                target = intent["data"].get("app_name") or intent["data"].get("command")
                if not target or len(target) < 2:
                    msg = f"Do you want me to {intent['type'].split('_')[0].lower()} something? Please specify."
                    print(f"SAMBA: {msg}")
                    if v_output: v_output.speak(msg)
                    continue

            context = memory.get_recent_context(n=3)
            
            # Optimization: Prevent LLM for short inputs or direct commands
            if intent["type"] == "CHAT" and (len(raw_input) < 5 or any(v in raw_input for v in ["open", "run", "launch", "close"])):
                msg = "I didn't catch that clearly. Please repeat."
                print(f"SAMBA: {msg}")
                if v_output: v_output.speak(msg)
                continue

            decision = decision_engine.decide(raw_input, intent, context)
            
            # 2. PLAN & EXECUTE Phase
            StateTracker.set_state(State.EXECUTING)
            
            if decision["action"] in ["EXECUTE", "MULTI"]:
                plan = planner.create_plan(raw_input, intent)
                
                if not plan:
                    print("SAMBA: I couldn't formulate a plan for that.")
                    continue

                if decision["action"] == "MULTI":
                    print("SAMBA: Processing multiple requests...")

                for step in plan:
                    time.sleep(0.3)
                    if SafetyLayer.is_dangerous(step):
                        print(f"SAMBA: Blocked dangerous part: {step}")
                        continue
                    
                    step_intent = intent_parser.detect_intent(step)
                    logger.start_timer("execution")
                    res = executor.execute(step_intent)
                    logger.end_timer("execution")
                    
                    clean_res = clean_text(res)
                    print(f"SAMBA: {clean_res}")
                    if v_output: v_output.speak(clean_res)
                    memory.add_interaction(step, res, step_intent["type"])
                    
                    # Pattern check for each step
                    pattern = memory.detect_patterns()
                    if pattern:
                        print(f"\nSAMBA: Pattern detected: {' -> '.join(pattern)}")
                        choice = input("Save as workflow? (yes/name/no): ").strip().lower()
                        if choice not in ["no", "n"]:
                            name = choice if choice != "yes" else input("Name: ").strip()
                            if name: memory.save_workflow(name, pattern)

            elif decision["action"] == "CHAT":
                logger.start_timer("brain")
                full_context = memory.get_context()
                response = brain.think(raw_input, full_context)
                logger.end_timer("brain")
                
                print(f"SAMBA: {clean_text(response)}")
                memory.add_interaction(raw_input, response, "CHAT")

            elif decision["action"] == "ASK":
                print("SAMBA: I'm not quite sure what you mean. Could you rephrase that?")

            # Performance Summary
            summary = logger.get_summary()
            if summary: 
                print(clean_text(summary))

        except KeyboardInterrupt:
            print("\nSAMBA: Goodbye, sir.")
            break
        except Exception as e:
            logger.error(f"Main Loop Error: {e}")
            print("SAMBA: I've encountered a system interruption. Please try again.")

if __name__ == "__main__":
    main()
