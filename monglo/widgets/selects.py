
from typing import Any

from .base import BaseWidget

class Select(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        choices = self.options.get("choices", [])
        if choices and isinstance(choices[0], (list, tuple)):
            choices = [{"value": v, "label": label} for v, label in choices]

        return {
            "type": "select",
            "choices": choices,
            "placeholder": self.options.get("placeholder", "Select an option"),
            "searchable": self.options.get("searchable", False),
        }

class MultiSelect(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        choices = self.options.get("choices", [])
        if choices and isinstance(choices[0], (list, tuple)):
            choices = [{"value": v, "label": label} for v, label in choices]

        return {
            "type": "multiselect",
            "choices": choices,
            "placeholder": self.options.get("placeholder", "Select options"),
            "searchable": self.options.get("searchable", True),
            "max_selections": self.options.get("max_selections"),
        }

class Autocomplete(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "autocomplete",
            "source_url": self.options.get("source_url", ""),
            "min_chars": self.options.get("min_chars", 2),
            "placeholder": self.options.get("placeholder", "Start typing..."),
            "display_field": self.options.get("display_field", "name"),
            "value_field": self.options.get("value_field", "_id"),
        }

class RadioButtons(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        choices = self.options.get("choices", [])
        if choices and isinstance(choices[0], (list, tuple)):
            choices = [{"value": v, "label": label} for v, label in choices]

        return {"type": "radio", "choices": choices, "inline": self.options.get("inline", True)}

class ReferenceSelect(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "reference_select",
            "collection": self.options.get("collection", ""),
            "display_field": self.options.get("display_field", "name"),
            "value_field": self.options.get("value_field", "_id"),
            "query": self.options.get("query", {}),
            "searchable": self.options.get("searchable", True),
            "placeholder": self.options.get("placeholder", "Select a reference"),
        }
