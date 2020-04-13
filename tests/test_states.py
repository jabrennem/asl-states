import pytest

from asl_states import (
    State,
    SucceedState,
    FailState,
    PassState
)


def test_state_init():
    state = State("MyState")
    assert state._state_dict == {"Type": None}


def test_succeed_state_init():
    succeed_state = SucceedState("MySucceed")
    assert succeed_state._state_dict == {"Type": "Succeed"}


def test_fail_state_init():
    fail_state = FailState("MyFail", cause="Invalid Parameters.", error="RuntimeError")
    assert fail_state._state_dict == {
        "Type": "Fail",
        "Cause": "Invalid Parameters.",
        "Error": "RuntimeError"
    }


def test_pass_state_init_next():
    pass_state_next = PassState("MyPass", next_state="TheNextStateId")
    assert pass_state_next.state_id == "MyPass"
    assert pass_state_next._state_dict == {"Type": "Pass", "Next": "TheNextStateId"}


def test_pass_state_init_end():
    pass_state_end = PassState("MyPass")
    assert pass_state_end.state_id == "MyPass"
    assert pass_state_end._state_dict == {"Type": "Pass", "End": True}
