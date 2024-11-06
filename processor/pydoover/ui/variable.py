from datetime import datetime

from typing import Union, Optional, Any

from .element import Element
from .misc import Range, Widget


class Variable(Element):
    type = "uiVariable"

    def __init__(
        self,
        name: str,
        display_name: str,
        var_type: str,
        curr_val: Any = None,
        precision: int = None,
        ranges: list[Union[Range, dict]] = None,
        earliest_data_time: Optional[datetime] = None,
        **kwargs
    ):
        # kwargs: verbose_str=verbose_str, show_activity=show_activity, form=form, graphic=graphic, layout=layout
        super().__init__(name, display_name, **kwargs)

        self.var_type = var_type
        self.curr_val = self._curr_val = curr_val
        self.precision = precision or kwargs.pop("dec_precision", None)
        self.earliest_data_time = earliest_data_time

        self.ranges = []
        if ranges is not None:
            self.add_ranges(*ranges)

    def to_dict(self):
        result = super().to_dict()
        result['type'] = self.type
        result['varType'] = self.var_type

        curr_val = self.current_value
        if curr_val is not None:
            result['currentValue'] = curr_val

        if self.precision is not None:
            result['decPrecision'] = self.precision

        if self.earliest_data_time is not None:
            if isinstance(self.earliest_data_time, datetime):
                result['earliestDataDate'] = int(self.earliest_data_time.timestamp())
            else:
                result['earliestDataDate'] = self.earliest_data_time

        result["ranges"] = [r.to_dict() for r in self.ranges]
        return result

    @property
    def current_value(self):
        return self._curr_val

    @current_value.setter
    def current_value(self, val):
        self.update(val)

    def update(self, new_value: Any):
        if self.precision is not None and new_value is not None:
            self._curr_val = round(new_value, self.precision)
        else:
            self._curr_val = new_value

    def add_ranges(self, *range_val: Range):
        for r in range_val:
            # still support legacy dict passing of range values.
            if isinstance(r, Range):
                self.ranges.append(r)
            elif isinstance(r, dict):
                self.ranges.append(Range.from_dict(r))


class NumericVariable(Variable):
    def __init__(
        self,
        name: str,
        display_name: str,
        curr_val: Union[int, float] = None,
        precision: int = None,
        ranges: list[Union[Range, dict]] = None,
        form: Union[Widget, str, None] = None,
        **kwargs
    ):
        super().__init__(
            name, display_name, var_type="float", curr_val=curr_val,
            precision=precision, ranges=ranges, **kwargs
        )
        self.form = form

    def to_dict(self):
        result = super().to_dict()
        if self.form is not None:
            result["form"] = self.form
        return result

class TextVariable(Variable):
    def __init__(self, name: str, display_name: str, curr_val: str = None, **kwargs):
        # fixme: double check this type
        super().__init__(name, display_name, var_type="string", curr_val=curr_val, **kwargs)


class BooleanVariable(Variable):
    def __init__(self, name: str, display_name: str, curr_val: bool = None, **kwargs):
        super().__init__(name, display_name, var_type="bool", curr_val=curr_val, **kwargs)


class DateTimeVariable(Variable):
    def __init__(self, name: str, display_name: str, curr_val: Union[datetime, int] = None, **kwargs):
        # fixme: double check this type, and how to handle different date / time / datetime
        super().__init__(name, display_name, var_type="time", curr_val=curr_val, **kwargs)


doover_ui_variable = Variable
