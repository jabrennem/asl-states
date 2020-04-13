import json


class SimpleStateChain:

    def __init__(self, states: list) -> None:
        self._states = states

    def __add__(self, state_chain):
        """Append two state chains."""
        left_states = self._states.copy()
        right_states = state_chain._states.copy()
        if left_states and right_states:
            if left_states[-1].is_terminal():
                raise RuntimeError("Cannot add two state chain to a chain with an existing terminal state.")
            left_states[-1].set_next_state(right_states[0].state_id)
        return SimpleStateChain(left_states + right_states)

    def _initial_state_id(self) -> str:
        try:
            return self._states[0].state_id
        except IndexError:
            return -1
    
    def json(self, branch: bool=True, indent: int=4) -> str:
        d = self.branch if branch else self.chain
        return json.dumps(d, indent=indent)
    
    @property
    def branch(self) -> dict:
        start_at = self._initial_state_id()
        if start_at == -1:
            return {}
        return {
            "StartAt": start_at,
            "States": self.chain
        }
    
    @property
    def chain(self) -> dict:
        """Convert states into a dict where there ids are keys and _state_dict objects are values."""
        chain = {}
        for state in self._states:
            chain[state.state_id] = state._state_dict
        return chain


class LinearStateChain:

    def __init__(self, states: list) -> None:
        self._states = states
    
    @property
    def chain(self):
        """Link all states to each other in succession.
        If the state is terminal, skip it.
        """
        chain = {}
        for i, state in enumerate(self._states):
            if not state.is_terminal():
                if i == len(self._states)-1:
                    state.set_as_end()
                else:
                    state.set_next_state(self._states[i+1].state_id)
            chain[state.state_id] = state._state_dict
        return chain
