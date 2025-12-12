
from __future__ import annotations

from typing import Any

from bson import DBRef, ObjectId
from bson.errors import InvalidId

from .base import BaseField

class ObjectIdField(BaseField):

    def validate(self, value: Any) -> ObjectId:
        if isinstance(value, ObjectId):
            return value

        if isinstance(value, str):
            try:
                return ObjectId(value)
            except InvalidId:
                raise ValueError(f"Invalid ObjectId: {value}") from None

        raise ValueError("Value must be an ObjectId or valid ObjectId string")

    def get_widget_config(self) -> dict[str, Any]:
        return {"type": "text", "readonly": self.readonly, "format": "objectid"}

class DBRefField(BaseField):

    def __init__(self, *, collection: str, database: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.collection = collection
        self.database = database

    def validate(self, value: Any) -> DBRef:
        if isinstance(value, DBRef):
            return value

        if isinstance(value, ObjectId):
            return DBRef(self.collection, value, self.database)

        if isinstance(value, str):
            try:
                oid = ObjectId(value)
                return DBRef(self.collection, oid, self.database)
            except InvalidId:
                raise ValueError(f"Invalid ObjectId for DBRef: {value}") from None

        raise ValueError("Value must be DBRef, ObjectId, or ObjectId string")

    def get_widget_config(self) -> dict[str, Any]:
        return {"type": "reference", "readonly": self.readonly, "collection": self.collection}
