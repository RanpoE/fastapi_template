from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/")
async def basic():
    try:
        return {
            "message": "Sekai"
        }
    except Exception as e:
        raise HTTPException(e)
