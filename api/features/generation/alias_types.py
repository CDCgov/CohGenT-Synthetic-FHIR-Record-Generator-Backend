# Alias for Distributions and Patient Row.
type Distributions = dict[str, list[str]]
type PatientRow = dict[tuple[str, str], str | bool]
type Code = str