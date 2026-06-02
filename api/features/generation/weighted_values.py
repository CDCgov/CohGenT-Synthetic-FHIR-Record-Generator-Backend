from decimal import Decimal
from api.models.value_types import ValueWeights
from random import choices

def distribute_weighted_values(count: int, setting_values: ValueWeights):
    '''
    This function is used for generating population distributions.
    '''
    values, weights = get_values_and_weights_as_lists(setting_values)
    return choices(values, weights=weights, k=count)

def select_from_weighted_list(setting_values: ValueWeights):
    values, weights = get_values_and_weights_as_lists(setting_values)
    selected_choice = choices(values, weights=weights, k=1)[0]
    return selected_choice

def get_values_and_weights_as_lists(valueWeights: ValueWeights):
    values: list[str] = [x.value for x in valueWeights.values]
    weights: list[int | float | Decimal] = [x.weight for x in valueWeights.values]
    return values, weights