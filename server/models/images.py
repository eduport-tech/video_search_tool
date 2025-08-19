from pydantic import BaseModel
from typing import Optional


class Dimensions(BaseModel):
    width: int
    height: int

class ImageUploadResponse(BaseModel):
    status: str
    url: str
    file_id: str

class ImageDetailsResponse(BaseModel):
    status: str
    url: str
    file_id: str
    mime_type: str
    file_size: int
    dimensions: Dimensions
    original_file_name: Optional[str] = None