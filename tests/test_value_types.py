from api.models.value_types import ValueWeights, ValueWeight, is_value_weights, is_value_weight
from decimal import Decimal

def test_value_weight_1() -> None:
    test: ValueWeight = ValueWeight.model_validate({"value": "str", "weight": 0.5})
    assert is_value_weight(test)

def test_value_weight_error_1() -> None:
    test = ("str", "str2")
    assert not is_value_weight(test)

def test_value_weight_error_2() -> None:
    test = ("str", 0.5, "str2")
    assert not is_value_weight(test)

def test_value_weights_type_check() -> None:
    test = ValueWeights.model_validate({
        "values": [
            {"value": "str", "weight": 0.5},
            {"value": "str2", "weight": 0.2}
        ]
    }) # Correct structure, fully model validated.
    assert(is_value_weights(test))

def test_value_weights_type_check_fail_1() -> None:
    test = { # type: ignore
        "values": [
            {"value": "str", "weight": 0.5},
            {"value": "str2", "weight": 0.2}
        ]
    } # Correct structure but not validated as type
    assert not is_value_weights(test) # type: ignore

def test_value_weights_type_check_decimal() -> None:
    test: ValueWeights = ValueWeights.model_validate({
        "values": [
            {"value": "str", "weight": Decimal(0.5)},
            {"value": "str2", "weight": Decimal(0.2)}
        ]
    }) # Correct structure with Decimal object
    assert is_value_weights(test)