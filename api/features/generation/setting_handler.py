
from api.models.cohort_settings import Setting
from api.models.field import Field


def find_setting(field: Field, user_settings: list[Setting] | None, default_settings: list[Setting]) -> Setting | None:
    field_setting = None
    if user_settings is not None:
        # First, attempt to find a user driven setting.
        field_setting = _find_setting(field, user_settings)
    if field_setting is None:
        # If no user driven setting, find the default setting.
        field_setting = _find_setting(field, default_settings)
    if field_setting is None:
        # If no default setting found, well... this ain't gonna work.
        raise ValueError(f"Default field setting for {field.path} missing.")
    return field_setting

def _find_setting(field: Field, settings: list[Setting]) -> Setting | None:
    setting = next((setting for setting in settings if setting.rule_id == field.user_setting_rule_id), None)
    return setting