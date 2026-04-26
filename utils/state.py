from enum import Enum, auto

class State(Enum):
    IDLE = auto()
    THINKING = auto()
    EXECUTING = auto()

class StateTracker:
    _state = State.IDLE

    @classmethod
    def set_state(cls, new_state: State):
        cls._state = new_state
        # Silent logging for state changes
        # print(f"[STATE] -> {new_state.name}")

    @classmethod
    def get_state(cls) -> State:
        return cls._state
