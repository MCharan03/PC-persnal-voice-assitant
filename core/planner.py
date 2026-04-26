class Planner:
    def __init__(self, memory=None):
        self.memory = memory

    def create_plan(self, user_input: str, intent: dict) -> list:
        """Breaks down intent into a list of executable steps."""
        intent_type = intent.get("type")
        
        if intent_type == "MULTI":
            return intent.get("commands", [])
        
        if intent_type == "WORKFLOW":
            workflow_name = intent.get("data", {}).get("name")
            return self.memory.get_workflow(workflow_name) or []
        
        if intent_type in ["OPEN_APP", "RUN_COMMAND"]:
            return [user_input]
            
        return []
