
from __future__ import annotations

from typing import Any, BinaryIO
from io import BytesIO

from .base import BaseField

class FileField(BaseField):
    
    def __init__(
        self,
        allowed_extensions: list[str] | None = None,
        max_size_mb: float | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.allowed_extensions = allowed_extensions or []
        self.max_size_mb = max_size_mb
    
    def validate(self, value: Any) -> bool:
        # Value should be a file-like object or file metadata
        if value is None:
            return not self.required
        
        if isinstance(value, dict):
            if "filename" in value and "file_id" in value:
                return True
        
        if hasattr(value, 'read'):
            return True
        
        return False
    
    def serialize(self, value: Any) -> dict | None:
        if value is None:
            return None
        
        # If already serialized metadata
        if isinstance(value, dict) and "filename" in value:
            return value
        
        return {
            "type": "file",
            "uploaded": True
        }
    
    def get_widget_config(self) -> dict[str, Any]:
        return {
            "type": "file",
            "allowed_extensions": self.allowed_extensions,
            "max_size_mb": self.max_size_mb,
            "accept": ",".join(self.allowed_extensions) if self.allowed_extensions else "*"
        }

class ImageField(FileField):
    
    def __init__(
        self,
        max_width: int | None = None,
        max_height: int | None = None,
        **kwargs
    ):
        # Default to common image formats
        if 'allowed_extensions' not in kwargs:
            kwargs['allowed_extensions'] = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        super().__init__(**kwargs)
        self.max_width = max_width
        self.max_height = max_height
    
    def get_widget_config(self) -> dict[str, Any]:
        config = super().get_widget_config()
        config.update({
            "type": "image",
            "max_width": self.max_width,
            "max_height": self.max_height,
            "preview": True
        })
        return config

class GridFSHelper:
    
    def __init__(self, database):
        from motor.motor_asyncio import AsyncIOMotorGridFSBucket
        self.fs = AsyncIOMotorGridFSBucket(database)
    
    async def upload_file(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: str | None = None,
        metadata: dict | None = None
    ) -> str:
        if isinstance(file_data, bytes):
            file_data = BytesIO(file_data)
        
        # Upload to GridFS
        file_id = await self.fs.upload_from_stream(
            filename,
            file_data,
            metadata={
                "content_type": content_type,
                **(metadata or {})
            }
        )
        
        return str(file_id)
    
    async def download_file(self, file_id: str) -> bytes:
        from bson import ObjectId
        
        grid_out = await self.fs.open_download_stream(ObjectId(file_id))
        data = await grid_out.read()
        return data
    
    async def delete_file(self, file_id: str) -> None:
        from bson import ObjectId
        await self.fs.delete(ObjectId(file_id))
    
    async def get_file_metadata(self, file_id: str) -> dict:
        from bson import ObjectId
        
        grid_out = await self.fs.open_download_stream(ObjectId(file_id))
        
        return {
            "file_id": str(file_id),
            "filename": grid_out.filename,
            "length": grid_out.length,
            "upload_date": grid_out.upload_date,
            "content_type": grid_out.metadata.get("content_type") if grid_out.metadata else None,
            "metadata": grid_out.metadata
        }
