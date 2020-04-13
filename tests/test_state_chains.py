import pytest

from asl_states import (
    PassState,
    SucceedState,
    FailState,
    LambdaState,
    ParallelState,
    SimpleBoolChoiceState,
    LinearStateChain,
    SimpleStateChain
)


def test_state_chain_all_pass_states():
    states = [PassState(f"MyPass{i}") for i in range(3)]
    state_chain = LinearStateChain(states)
    assert state_chain.chain == {
        "MyPass0": {"Type": "Pass", "Next": "MyPass1"},
        "MyPass1": {"Type": "Pass", "Next": "MyPass2"},
        "MyPass2": {"Type": "Pass", "End": True}
    }


def test_state_chain_pass_succeed_states():
    state_chain = LinearStateChain([PassState("Pass1"), PassState("Pass2"), SucceedState("Succeeded")])
    assert state_chain.chain == {
        "Pass1": {"Type": "Pass", "Next": "Pass2"},
        "Pass2": {"Type": "Pass", "Next": "Succeeded"},
        "Succeeded": {"Type": "Succeed"}
    }


def test_state_chain_pass_failed_states():
    state_chain = LinearStateChain([PassState("Pass1"), PassState("Pass2"), FailState("Failed")])
    assert state_chain.chain == {
        "Pass1": {"Type": "Pass", "Next": "Pass2"},
        "Pass2": {"Type": "Pass", "Next": "Failed"},
        "Failed": {"Type": "Fail"}
    }


def test_simple_bool_choice_state():
    choice_state = SimpleBoolChoiceState("MyStep", "$.run_step", "RunSmStep", "Succeed")
    assert choice_state._state_dict == {
        'Type': 'Choice', 
        'Choices': [
            {
                'Variable': '$.run_step', 
                'BooleanEquals': True, 
                'Next': 'RunSmStep'
            }, 
            {
                'Variable': '$.run_step', 
                'BooleanEquals': False, 
                'Next': 'Succeed'
            }], 
        'Default': 'RunSmStep'
    }


def test_parallel_state():
    """Test creation of a parallel state running two simulataneous simple state chains."""
    pass1, bool1, succeeded, failed = "Pass1", "Bool1", "Succeeded", "Failed"
    sc1 = SimpleStateChain([PassState(pass1, next_state=bool1), SimpleBoolChoiceState(bool1, "$.is_true", succeeded, failed), SucceedState(succeeded), FailState(failed)])
    sc2 = SimpleStateChain([PassState(pass1, next_state=bool1), SimpleBoolChoiceState(bool1, "$.is_true", succeeded, failed), SucceedState(succeeded), FailState(failed)])
    parallel_state = ParallelState("ParallelState", state_chains=[sc1, sc2])
    assert parallel_state._state_dict == {'Type': 'Parallel', 'End': True, 'Branches': [{'StartAt': 'Pass1', 'States': {'Pass1': {'Type': 'Pass', 'Next': 'Bool1'}, 'Bool1': {'Type': 'Choice', 'Choices': [{'Variable': '$.is_true', 'BooleanEquals': True, 'Next': 'Succeeded'}, {'Variable': '$.is_true', 'BooleanEquals': False, 'Next': 'Failed'}], 'Default': 'Succeeded'}, 'Succeeded': {'Type': 'Succeed'}, 'Failed': {'Type': 'Fail'}}}, {'StartAt': 'Pass1', 'States': {'Pass1': {'Type': 'Pass', 'Next': 'Bool1'}, 'Bool1': {'Type': 'Choice', 'Choices': [{'Variable': '$.is_true', 'BooleanEquals': True, 'Next': 'Succeeded'}, {'Variable': '$.is_true', 'BooleanEquals': False, 'Next': 'Failed'}], 'Default': 'Succeeded'}, 'Succeeded': {'Type': 'Succeed'}, 'Failed': {'Type': 'Fail'}}}]}


def test_lambda_state():
    lambda_state = LambdaState("MyLambda", "submit_job", {"MyBool": True})
    assert lambda_state._state_dict == {
        'Type': 'Task', 
        'End': True, 
        'Resource': 'arn:aws:states:::lambda:invoke', 
        'Parameters': {
            'FunctionName': 'submit_job', 
            'Payload': {'MyBool': True}
    }}


def test_simple_state_chain():
    pass1, pass2 = "Pass1", "Pass2", 
    bool1 = "Bool1"
    succeeded, failed = "Succeeded", "Failed"
    states = [
        PassState(pass1, next_state=pass2),
        PassState(pass2, next_state=bool1),
        SimpleBoolChoiceState(bool1, "$.is_true", succeeded, failed),
        SucceedState(succeeded), 
        FailState(failed)
    ]
    state_chain = SimpleStateChain(states)
    assert state_chain.chain == {
        'Pass1': {'Type': 'Pass', 'Next': 'Pass2'}, 
        'Pass2': {'Type': 'Pass', 'Next': 'Bool1'}, 
        'Bool1': {'Type': 'Choice', 'Choices': [{'Variable': '$.is_true', 'BooleanEquals': True, 'Next': 'Succeeded'}, {'Variable': '$.is_true', 'BooleanEquals': False, 'Next': 'Failed'}], 'Default': 'Succeeded'}, 
        'Succeeded': {'Type': 'Succeed'}, 
        'Failed': {'Type': 'Fail'}
    }


def test_simple_state_chain_branch():
    pass1, pass2 = "Pass1", "Pass2", 
    bool1 = "Bool1"
    succeeded, failed = "Succeeded", "Failed"
    states = [
        PassState(pass1, next_state=pass2),
        PassState(pass2, next_state=bool1),
        SimpleBoolChoiceState(bool1, "$.is_true", succeeded, failed),
        SucceedState(succeeded), 
        FailState(failed)
    ]
    state_chain = SimpleStateChain(states)
    assert state_chain.branch == {
        "StartAt": "Pass1",
        "States": {
            'Pass1': {'Type': 'Pass', 'Next': 'Pass2'}, 
            'Pass2': {'Type': 'Pass', 'Next': 'Bool1'}, 
            'Bool1': {'Type': 'Choice', 'Choices': [{'Variable': '$.is_true', 'BooleanEquals': True, 'Next': 'Succeeded'}, {'Variable': '$.is_true', 'BooleanEquals': False, 'Next': 'Failed'}], 'Default': 'Succeeded'}, 
            'Succeeded': {'Type': 'Succeed'}, 
            'Failed': {'Type': 'Fail'}
        }
    }


def test_simple_state_chain_add_empty_empty():
    sc1, sc2 = SimpleStateChain([]), SimpleStateChain([])
    sc3 = sc1 + sc2
    assert sc3._states == []


def test_simple_state_chain_add_one_full_one_empty():
    pass_state = PassState("Pass1")
    sc1, sc2 = SimpleStateChain([pass_state]), SimpleStateChain([])
    sc3 = sc1 + sc2
    assert sc3._states == [pass_state]

    sc1, sc2 = SimpleStateChain([]), SimpleStateChain([pass_state])
    sc3 = sc1 + sc2
    assert sc3._states == [pass_state]


def test_simple_state_chain_add_left_contains_terminal_state():
    with pytest.raises(RuntimeError):
        SimpleStateChain([SucceedState("succeed")]) + SimpleStateChain([PassState("pass2")])
        SimpleStateChain([FailState("fail")]) + SimpleStateChain([PassState("pass2")])


def test_simple_state_chain_task_error_handle():
    lambda_state = LambdaState("Lambda", "my-lambda", {}, next_state="Succeed", catch_all_state="Fail")
    fail_state = FailState("Fail", "Lambda function failed", "LambdaError")
    sc = SimpleStateChain([lambda_state, SucceedState("Succeed"), fail_state])
    assert sc.chain == {
        'Lambda': {
            'Type': 'Task', 
            'Next': 'Succeed', 
            'Resource': 'arn:aws:states:::lambda:invoke', 
            'Parameters': {
                'FunctionName': 'my-lambda', 
                'Payload': {}
            }, 
            'Catch': [{'ErrorEquals': ['States.ALL'], 'Next': 'Fail'}]
        }, 
        'Succeed': {'Type': 'Succeed'}, 
        'Fail': {'Type': 'Fail', 'Cause': 'Lambda function failed', 'Error': 'LambdaError'}}
