class State:
    """Every state has a type and possibly more fields."""

    _state_type = None
    _terminal = False

    def __init__(self, state_id: str) -> None:
        self.state_id = state_id
        self._fields = {"Type": self._state_type}
    
    def is_terminal(self):
        return self._terminal

    @property
    def _state_dict(self) -> dict:
        return self._fields

    def update_fields(self, new_fields: dict) -> None:
        for field, field_value in new_fields.items():
            if field_value is not None:
                self._fields[field] = field_value
    
    def delete_field(self, field: str) -> None:
        if field in self._fields:
            del self._fields[field]


class SucceedState(State):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-succeed-state.html"""
    _state_type = "Succeed"
    _terminal = True


class FailState(State):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-fail-state.html"""
    _state_type = "Fail"
    _terminal = True

    def __init__(self, state_id: str, cause: str=None, error: str=None):
        super().__init__(state_id)
        self._cause = cause
        self._error = error
        self.update_fields({"Cause": self._cause, "Error": self._error})


class TransitionState(State):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-common-fields.html"""

    def set_next_state(self, next_state: str) -> None:
        self.update_fields({"Next": next_state})
        self.delete_field("End")
    
    def set_as_end(self):
        self.delete_field("Next")
        self.update_fields({"End": True})
    
    def __init__(self, state_id: str, next_state: str=None, comment: str=None, input_path=None, output_path=None) -> None:
        """Define variables and update _fields with new fields."""
        super().__init__(state_id)
        new_fields = {
            "Comment": comment,
            "InputPath": input_path,
            "OutputPath": output_path
        }
        if next_state:
            new_fields["Next"] = next_state
        else:
            new_fields["End"] = True
        self.update_fields(new_fields)


class PassState(TransitionState):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-pass-state.html"""
    _state_type = "Pass"


class SimpleBoolChoiceState(State):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html"""
    _state_type = "Choice"
    _is_split = True

    def __init__(self, state_id: str, variable: str, pos_next: str, neg_next: str) -> None:
        super().__init__(state_id)
        choices = self._create_choices(variable, pos_next, neg_next)
        self.update_fields({
            "Choices": choices,
            "Default": pos_next
        })
    
    def _create_choices(self, var: str, pos_next: str, neg_next: str) -> list:
        choice = lambda x, y, z: {"Variable": x, "BooleanEquals": y, "Next": z}
        return [choice(var, True, pos_next), choice(var, False, neg_next)]
    
    @property
    def is_split(self):
        return self._is_split


class ParallelState(TransitionState):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-parallel-state.html"""
    _state_type = "Parallel"

    def __init__(self, state_id: str, state_chains: list, result=None, result_path=None, **kwargs) -> None:
        super().__init__(state_id, **kwargs)
        branches = [state_chain.branch for state_chain in state_chains]
        self.update_fields({
            "Branches": branches,
            "Result": result,
            "ResultPath": result_path
        })


class TaskState(TransitionState):
    """https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-task-state.html"""
    _state_type = "Task"

    def __init__(self, state_id: str, resource: str, parameters: dict=None, result=None, result_path=None, retry: list=None, catch: list=None, catch_all_state: str=None, timeout_seconds: int=None, heartbeat_seconds: int=None, **kwargs):
        super().__init__(state_id, **kwargs)
        if not resource.startswith("arn:"):
            raise ValueError("resource must start with 'arn:'.")
        if catch_all_state:
            catch = [{
                "ErrorEquals": ["States.ALL"],
                "Next": catch_all_state
            }]
        self.update_fields({
            "Resource": resource,
            "Parameters": parameters,
            "Result": result,
            "ResultPath": result_path,
            "Retry": retry,
            "Catch": catch,
            "TimeoutSeconds": timeout_seconds,
            "HeartbeatSeconds": heartbeat_seconds
        })


class LambdaState(TaskState):

    def __init__(self, state_id: str, function_name: str, payload: dict, **kwargs):
        super().__init__(state_id, "arn:aws:states:::lambda:invoke", {
            "FunctionName": function_name,
            "Payload": payload
        }, **kwargs)