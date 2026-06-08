from decimal import Decimal
from typing import Literal, TypeVar, overload
from api.models.cohort_settings import MedicationSet
from api.models.value_types import ValueWeights
from random import choices

T = TypeVar('T')

def distribute_weighted_values(count: int, setting_values: ValueWeights):
    '''
    Genenerating a distribution (e.g., patient race/ethnicity).
    '''
    values, weights = _get_values_and_weights_as_lists(setting_values)
    return choices(values, weights=weights, k=count)

def select_from_weighted_list(setting_values: ValueWeights):
    """
    Select a single item from a weighted list.
    """
    values, weights = _get_values_and_weights_as_lists(setting_values)
    selected_choice = choices(values, weights=weights)[0]
    return selected_choice

def select_medication_set(medication_sets: list[MedicationSet]) -> MedicationSet:
    weights: list[int | float | Decimal] = [x.weight for x in medication_sets]
    return _weighted_choice(medication_sets, weights)


@overload
def _weighted_choice(items: list[T], weights: list[int | float | Decimal], k: Literal[1] = 1) -> T: ...

@overload
def _weighted_choice(items: list[T], weights: list[int | float | Decimal], k: int) -> list[T]: ...

def _weighted_choice(items: list[T], weights: list[int | float | Decimal], k: int = 1) -> T | list[T]:
    """Internal helper for weighted random selection."""
    selected = choices(items, weights=weights, k=k)
    return selected[0] if k == 1 else selected

def _get_values_and_weights_as_lists(valueWeights: ValueWeights):
    """Extract values and weights from ValueWeights structure."""
    values: list[str] = [x.value for x in valueWeights.values]
    weights: list[int | float | Decimal] = [x.weight for x in valueWeights.values]
    return values, weights