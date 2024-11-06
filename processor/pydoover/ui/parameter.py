from typing import Union
from datetime import datetime

from .interaction import Interaction, NotSet


class Parameter(Interaction):
    type = NotImplemented


class NumericParameter(Parameter):
    type = "uiFloatParam"

    def __init__(
        self, name, display_name, min_val: Union[int, float] = None, max_val: Union[int, float] = None, **kwargs
    ):
        super().__init__(name, display_name, **kwargs)

        self.min = min_val or kwargs.pop("float_min", None)
        self.max = max_val or kwargs.pop("float_max", None)

    def to_dict(self):
        result = super().to_dict()

        if self.min is not None:
            result['min'] = self.min
        if self.max is not None:
            result['max'] = self.max

        return result


class TextParameter(Parameter):
    type = "uiTextParam"

    def __init__(self, name, display_name, is_text_area: bool = False, **kwargs):
        super().__init__(name, display_name, **kwargs)
        self.is_text_area = is_text_area

    def to_dict(self):
        result = super().to_dict()
        result['isTextArea'] = self.is_text_area
        return result


class BooleanParameter(Parameter):
    type = "uiBoolParam"

    def __init__(self, name, display_name, **kwargs):
        super().__init__(name, display_name, **kwargs)
        raise NotImplementedError("boolean parameter not implemented in doover site.")


class DateTimeParameter(Parameter):
    """Datetime is stored as epoch seconds UTC"""
    type = "uiDatetimeParam"

    def __init__(self, name: str, display_name: str, include_time: bool = False, **kwargs):
        super().__init__(name, display_name, **kwargs)
        self.include_time = include_time

    @property
    def current_value(self):
        if self._current_value is NotSet or self._current_value is None:
            return None
        if isinstance(self._current_value, datetime):
            return self._current_value
        elif isinstance(self._current_value, (int, float)):
            return datetime.utcfromtimestamp(self._current_value)
        return None
    
    @current_value.setter
    def current_value(self, new_val):
        if isinstance(new_val, datetime):
            new_val = int(new_val.timestamp())
        self._current_value = new_val

    def to_dict(self):
        result = super().to_dict()
        result['includeTime'] = self.include_time
        return result


doover_ui_float_parameter = NumericParameter
doover_ui_text_parameter = TextParameter
doover_ui_datetime_parameter = DateTimeParameter


def numeric_parameter(
    name: str, display_name: str, min_val: Union[int, float] = None, max_val: Union[int, float] = None, **kwargs
):
    def decorator(func):
        func._ui_type = NumericParameter
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "min_val": min_val,
            "max_val": max_val,
            **kwargs,
        }
        return func
    return decorator

def text_parameter(name: str, display_name: str, is_text_area: bool = False, **kwargs):
    def decorator(func):
        func._ui_type = TextParameter
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "is_text_area": is_text_area,
            **kwargs,
        }
        return func
    return decorator


def boolean_parameter(name: str, display_name: str, **kwargs):
    def decorator(func):
        func._ui_type = BooleanParameter
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            **kwargs,
        }
        return func
    return decorator


def datetime_parameter(name: str, display_name: str, include_time: bool = False, **kwargs):
    def decorator(func):
        func._ui_type = DateTimeParameter
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "include_time": include_time,
            **kwargs
        }
        return func
    return decorator
