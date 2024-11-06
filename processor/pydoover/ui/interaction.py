import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from .element import Element
from .misc import Colour, Option


if TYPE_CHECKING:
    from .manager import UIManager

log = logging.getLogger(__name__)


class NotSet:
    pass


class Interaction(Element):
    type = "uiInteraction"

    def __init__(
        self, name: str, display_name: str = None, current_value: Any = NotSet,
        default: Any = None, callback=None, transform_check=None, show_activity: Optional[bool] = None, **kwargs
    ):
        super().__init__(name, display_name, **kwargs)
        self._current_value = current_value
        self._default_value = default or kwargs.pop("default_val", None)

        self._manager: Optional["UIManager"] = None

        if callback:
            self.callback = callback
        if transform_check:
            self.transform_check = transform_check

        if self._current_value in (None, NotSet) and self._default_value is not None:
            print(f"Coercing {self.name} to default value {self._default_value}")
            self.coerce(self._default_value)

        self.show_activity = show_activity

    @property
    def current_value(self):
        return self._current_value if self._current_value is not NotSet else None

    @current_value.setter
    def current_value(self, new_val):
        ## Store all datetime objects as epoch seconds internally
        if isinstance(new_val, datetime):
            new_val = int(new_val.timestamp())
        self._current_value = new_val

    def _json_safe_current_value(self):
        result = self.current_value
        if isinstance(result, datetime):
            return int(result.timestamp())
        return result

    def callback(self, new_value: Any):
        return

    def transform_check(self, new_value: Any) -> Any:
        """Transform and check a new value before setting it.

        This is called before any callback functions are invoked.

        By default, this will replace any None values with a set default value.
        """
        if new_value is None and self._default_value is not None:
            return self._default_value
        else:
            return new_value

    def _handle_new_value(self, new_value: Any):
        try:
            new_value = self.transform_check(new_value)
        except Exception as e:
            log.error(f"Error transforming value for {self.name}: {e}")
            return

        self.current_value = new_value

        try:
            self.callback(new_value)
        except Exception as e:
            log.error(f"Error in callback for {self.name}: {e}")

    def coerce(self, value: Any, critical: bool = False):
        if critical and self._manager and value != self.current_value:
            self._manager._has_critical_interaction_pending = True

        self.current_value = value

    def to_dict(self):
        res = super().to_dict()
        if self._current_value is not NotSet:
            res['currentValue'] = self._json_safe_current_value()
        if self.show_activity is not None:
            res['showActivity'] = self.show_activity
        return res


class Action(Interaction):
    type = "uiAction"

    def __init__(
        self, name: str, display_name: str, colour: Colour = Colour.blue, requires_confirm: bool = True, **kwargs
    ):
        super().__init__(name, display_name, **kwargs)
        self.colour = colour
        self.requires_confirm = requires_confirm

    def to_dict(self):
        result = super().to_dict()
        result['colour'] = str(self.colour)
        result['requiresConfirm'] = self.requires_confirm
        return result


class WarningIndicator(Interaction):
    type = "uiWarningIndicator"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_cancel = kwargs.pop("can_cancel", True)

    def to_dict(self):
        result = super().to_dict()
        result["can_cancel"] = self.can_cancel
        return result


class HiddenValue(Interaction):
    type = "uiHiddenValue"

    def __init__(self, name, **kwargs):
        super().__init__(name, display_name=None, **kwargs)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
        }


class SlimCommand(Interaction):
    type = "uiStateCommand"


class StateCommand(SlimCommand):
    type = "uiStateCommand"

    def __init__(self, name: str, display_name: str = None, user_options: list[Option] = None, **kwargs):
        super().__init__(name, display_name, **kwargs)

        # A list of doover_ui_element's
        self.user_options = []
        self.add_user_options(*user_options)

    def to_dict(self):
        result = super().to_dict()
        result["userOptions"] = {o.name: o.to_dict() for o in self.user_options}
        return result

    def add_user_options(self, *option: Option):
        for o in option:
            # still support legacy dict passing of option values.
            if isinstance(o, Option):
                self.user_options.append(o)
            elif isinstance(o, dict):
                self.user_options.append(Option.from_dict(o))

    add_user_option = add_user_options


class Slider(Interaction):
    type = "uiSlider"

    def __init__(self, name: str, display_name: str = None, min_val: int = 0, max_val: int = 100, step_size: float = 0.1,
                 dual_slider: bool = True, inverted: bool = True, icon: Optional[str] = None, **kwargs
        ):
        super().__init__(name, display_name, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step_size = step_size
        self.dual_slider = dual_slider
        self.inverted = inverted
        self.icon = icon

    def to_dict(self):
        result = super().to_dict()
        result["min"] = self.min_val
        result["max"] = self.max_val
        result["stepSize"] = self.step_size
        result["dualSlider"] = self.dual_slider
        result["isInverted"] = self.inverted
        result["icon"] = self.icon
        return result


doover_ui_interaction = Interaction
doover_ui_action = Action
doover_ui_state_command = StateCommand
doover_ui_warning_indicator = WarningIndicator
doover_ui_hidden_value = HiddenValue
doover_ui_slider = Slider


def action(name: str, display_name: str = None, colour: Colour = Colour.blue, requires_confirm: bool = True, **kwargs):
    def decorator(func):
        func._ui_type = Action
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "colour": colour,
            "requires_confirm": requires_confirm,
            **kwargs
        }
        return func
    return decorator


def warning_indicator(name: str, display_name: str = None, can_cancel: bool = True, **kwargs):
    def decorator(func):
        func._ui_type = WarningIndicator
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "can_cancel": can_cancel,
            **kwargs,
        }
        return func
    return decorator


def state_command(name: str, display_name: str = None, user_options: list[Option] = None, **kwargs):
    def decorator(func):
        func._ui_type = StateCommand
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "user_options": user_options,
            **kwargs,
        }
        return func
    return decorator


def hidden_value(name: str, **kwargs):
    def decorator(func):
        func._ui_type = HiddenValue
        func._ui_kwargs = {
            "name": name,
            **kwargs,
        }
        return func
    return decorator


def slider(name: str, display_name: str = None, min_val: int = 0, max_val: int = 100, step_size: float = 0.1,
        dual_slider: bool = True, inverted: bool = True, icon: Optional[str] = None, **kwargs):
    def decorator(func):
        func._ui_type = Slider
        func._ui_kwargs = {
            "name": name,
            "display_name": display_name,
            "min_val": min_val,
            "max_val": max_val,
            "step_size": step_size,
            "dual_slider": dual_slider,
            "inverted": inverted,
            "icon": icon,
            **kwargs,
        }
        return func
    return decorator
