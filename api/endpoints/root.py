from fastapi import APIRouter, HTTPException, File, UploadFile
from ultralytics import YOLO
import base64
from pydantic import BaseModel, EmailStr


class UpdateProfileSchema(BaseModel):
    """Models updatable field of a profile instance"""

    image: str


model = YOLO("ml-models/yolov8n.pt")
router = APIRouter()


@router.post("/")
async def basic():
    try:
        return {"message": "Sekai"}
    except Exception as e:
        raise HTTPException(e)


@router.post("/upload")
async def handle_upload(photo: UploadFile = File(...)):
    results = model(photo.filename)
    name_list = model.names

    items = {}
    for r in results:
        boxes = r.boxes

        for box in boxes:
            label = str(name_list.get(box.cls.item()))

            items[label] = items[label] + 1 if items.get(label) else 1

    return items


@router.post("/upload64")
def handle_upload_64(payload: UpdateProfileSchema):
    file_name = "uploaded_image.png"
    data_split = payload.image.split("base64,")
    encoded_data = data_split[1]
    data = base64.b64decode(encoded_data)
    with open(file_name, "wb") as writer:
        writer.write(data)

    results = model(file_name)
    name_list = model.names

    items = {}
    for r in results:
        boxes = r.boxes

        for box in boxes:
            label = str(name_list.get(box.cls.item()))

            items[label] = items[label] + 1 if items.get(label) else 1

    return items
