import inspect
from typing import Any, Optional

from .element import Element


class Container(Element):
    type = "uiContainer"

    def __init__(self, name, display_name=None, children: list[Element] = None, status_icon: str = None, auto_add_elements: bool = True, **kwargs):
        super().__init__(name, display_name, **kwargs)

        # A list of doover_ui_elements
        self._children = dict()
        self.add_children(*children or [])

        self.status_icon = status_icon

        self._register_interactions()
        if auto_add_elements:
            self.add_children(*[e for name, e in inspect.getmembers(self, predicate=lambda e: isinstance(e, Element))])

        self._max_position = 0

    def _register_interactions(self):
        for name, func in inspect.getmembers(self, predicate=lambda f: inspect.ismethod(f) and hasattr(f, "_ui_type")):
            item = func._ui_type(**func._ui_kwargs)
            item.callback = func
            setattr(self, func.__name__, item)

    def to_dict(self):
        result = super().to_dict()

        if self.status_icon is not None:
            result['statusIcon'] = self.status_icon

        result["children"] = {name: c.to_dict() for name, c in self._children.items()}
        return result

    def get_diff(self, other: dict[str, Any], remove: bool = True) -> Optional[dict[str, Any]]:
        res = super().get_diff(other, remove=remove) or {}
        # this will account for all the "normal" attributes, but not the children, since dicts aren't hashable
        # (ie. you can't do dict1 == dict2 to see if they're equal)
        other_children = other.get("children", {})
        this_children = {name: c for name, c in self._children.items()}

        children_diff = dict()
        if remove:
            children_diff.update({k: None for k in other_children if k not in this_children})  # to_remove

        for name, child in this_children.items():
            try:
                diff = child.get_diff(other_children[name], remove=remove)
                if diff is not None:
                    children_diff[name] = diff
            except KeyError:
                children_diff[name] = child.to_dict()

        if children_diff:
            res["children"] = children_diff

        if len(res) == 0:
            return None

        return res

    @property
    def children(self):
        return list(self._children.values())

    def set_children(self, children: list[Element]):
        self._children.clear()
        self.add_children(*children)

    def add_children(self, *children: Element):
        for c in children:
            if not isinstance(c, Element):
                continue

            self._children[c.name] = c
            c.parent = self

            if not c.position:
                c.position = self._max_position
                self._max_position += 1

        return self

    def remove_children(self, *children: Element):
        for c in children:
            try:
                del self._children[c.name]
            except KeyError:
                pass

    def clear_children(self):
        self._children.clear()

    def get_element(self, element_name: str) -> Optional[Element]:
        try:
            return self._children[element_name]
        except KeyError:
            pass

        for element in self._children.values():
            if isinstance(element, Container):
                elem = element.get_element(element_name)
                if elem is not None:
                    return elem


class Submodule(Container):
    type = "uiSubmodule"

    def __init__(
        self, name: str, display_name: str, children: list[Element] = None, status: str = None, is_collapsed: bool = False, **kwargs
    ):
        super().__init__(name, display_name, children, **kwargs)

        self.status = status or kwargs.pop("status_string", None)
        self.collapsed = is_collapsed or kwargs.pop("collapsed", False)

    def to_dict(self):
        result = super().to_dict()
        if self.status is not None:
            result['statusString'] = self.status
        # result['isCollapsed'] = self.collapsed()

        return result


doover_ui_container = Container
doover_ui_submodule = Submodule
