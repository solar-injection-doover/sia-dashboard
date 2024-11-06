from typing import Union, Any


class Colour:
    blue = "blue"
    yellow = "yellow"
    red = "red"
    green = "green"
    magenta = "magenta"
    limegreen = "limegreen"
    tomato = "tomato"
    orange = "orange"
    purple = "purple"
    grey = "grey"

    @classmethod
    def from_hex(cls, hex_string):
        return hex_string

    @classmethod
    def from_string(cls, value):
        return value  # fixme: this hackiness


class Range:
    def __init__(
        self, label: str = None, min_val: Union[int, float] = None,
        max_val: Union[int, float] = None, colour: "Colour" = Colour.blue, show_on_graph: bool = True
    ):
        self.label = label
        self.min = min_val
        self.max = max_val
        self.colour = colour
        self.show_on_graph = show_on_graph

    def to_dict(self):
        to_return = {
            "min": self.min,
            "max": self.max,
            "colour": self.colour,
            "show_on_graph": self.show_on_graph,
        }
        if self.label:
            to_return["label"] = self.label
        return to_return

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(data.get("label"), data["min"], data["max"], Colour.from_string(data["colour"]), data["show_on_graph"])


class Option:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name

    def to_dict(self):
        return {
            "name": self.name,
            "displayString": self.display_name,
            "type": "uiElement",
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(data["name"], data["display_str"])


class Widget:
    linear = "linearGauge"
    radial = "radialGauge"

    @classmethod
    def from_string(cls, value):
        return value  # fixme: this hackiness