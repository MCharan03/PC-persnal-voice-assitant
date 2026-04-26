class DecisionEngine:
    def __init__(self, memory=None):
        self.memory = memory

    def decide(self, user_input: str, intent: dict, context: str) -> dict:
        """Rule-based decision logic to determine high-level action."""
        intent_type = intent.get("type")

        if intent_type == "MULTI":
            return {
                "action": "MULTI",
                "reason": "Input contains multiple commands."
            }
        
        if intent_type in ["OPEN_APP", "RUN_COMMAND", "WORKFLOW"]:
            return {
                "action": "EXECUTE",
                "reason": f"Input identified as {intent_type}."
            }
        
        if intent_type == "CHAT":
            return {
                "action": "CHAT",
                "reason": "Input identified as general conversation."
            }

        return {
            "action": "ASK",
            "reason": "Intent unclear."
        }
