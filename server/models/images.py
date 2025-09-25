from pydantic import BaseModel
from typing import Optional


class Dimensions(BaseModel):
    width: int
    height: int

class ImageUploadResponse(BaseModel):
    status: str
    url: str
    mime_type: str
    file_id: str

class ImageDetailsResponse(BaseModel):
    url: str
    id: str
    mime_type: str
    file_size: int
    dimensions: Dimensions
    original_file_name: Optional[str] = None

    @classmethod
    def from_image_data(cls, image_data):
        return cls(
            url=image_data.url,
            id=str(image_data.id),
            mime_type=image_data.mime_type,
            file_size=image_data.file_size,
            dimensions=Dimensions(width=image_data.width, height=image_data.height),
            original_file_name=image_data.original_file_name
        )