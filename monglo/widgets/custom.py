
from collections.abc import Callable
from typing import Any

from .base import BaseWidget

class CustomWidget(BaseWidget):

    def __init__(self, render_func: Callable | None = None, **options):
        super().__init__(**options)
        self.render_func = render_func

    def render_config(self) -> dict[str, Any]:
        if self.render_func:
            return self.render_func(self.options)

        return {
            "type": "custom",
            "component_name": self.options.get("component_name", "CustomWidget"),
            "props": self.options.get("props", {}),
            "events": self.options.get("events", {}),
        }

class WidgetGroup(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        widgets_config = []
        for name, widget in self.options.get("widgets", []):
            widgets_config.append({"name": name, "config": widget.render_config()})

        return {
            "type": "widget_group",
            "widgets": widgets_config,
            "layout": self.options.get("layout", "vertical"),
            "label": self.options.get("label", ""),
        }

class ConditionalWidget(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        widget = self.options.get("widget")
        widget_config = widget.render_config() if widget else {}

        return {
            "type": "conditional",
            "widget": widget_config,
            "condition": self.options.get("condition", {}),
            "show_when": self.options.get("show_when", "equals"),
        }
