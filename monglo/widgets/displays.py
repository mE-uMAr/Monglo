
from typing import Any

from .base import BaseWidget

class Label(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "label",
            "format": self.options.get("format", "normal"),  # normal, bold, italic
            "color": self.options.get("color"),
        }

class Badge(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "badge",
            "variant": self.options.get("variant", "default"),
            "color": self.options.get("color"),
            "rounded": self.options.get("rounded", True),
        }

class Link(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "link",
            "target": self.options.get("target", "_self"),
            "format": self.options.get("format", "url"),  # url, email
            "show_icon": self.options.get("show_icon", True),
        }

class Image(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "image",
            "width": self.options.get("width"),
            "height": self.options.get("height"),
            "thumbnail": self.options.get("thumbnail", True),
            "alt": self.options.get("alt", "Image"),
            "lazy_load": self.options.get("lazy_load", True),
        }

class JSONDisplay(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "json",
            "expanded": self.options.get("expanded", False),
            "highlight": self.options.get("highlight", True),
            "line_numbers": self.options.get("line_numbers", True),
        }

class CodeDisplay(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "code",
            "language": self.options.get("language", "text"),
            "theme": self.options.get("theme", "github"),
            "line_numbers": self.options.get("line_numbers", True),
            "copy_button": self.options.get("copy_button", True),
        }

class ProgressBar(BaseWidget):

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "progress",
            "min": self.options.get("min", 0),
            "max": self.options.get("max", 100),
            "show_value": self.options.get("show_value", True),
            "variant": self.options.get("variant", "default"),
        }
