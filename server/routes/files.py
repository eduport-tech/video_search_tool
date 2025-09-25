"""Files Route"""

from fastapi import (APIRouter,
                     Depends,
                     File,
                     HTTPException,
                     status,
                     UploadFile)
from server.utils.current_user import current_conversation_user, CurrentUser
from server.brain.image_questions import save_uploaded_image
from server.utils.image_processing import get_image_url
from server.models.images import ImageUploadResponse, ImageDetailsResponse

router = APIRouter(tags=["Files"], prefix="/files")


@router.post("/image_upload", response_model=ImageUploadResponse)
async def image_upload(file: UploadFile = File(...),
                       current_user: CurrentUser = Depends(current_conversation_user),
                       ):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No file uploaded.")
    response = await save_uploaded_image(
        image_file=file,
        user_id=current_user.user_id,
        file_name=file.filename
    )
    if response["status"] == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=response["message"])
    return response

@router.get("/uploaded_images/{file_id}", response_model=ImageDetailsResponse)
async def get_uploaded_image(file_id: str):
    response = await get_image_url(file_id)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Image not found.")
    return response