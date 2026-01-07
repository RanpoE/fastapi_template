from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field

from db.mongo import get_collection
from services.cloudinary_service import upload_image_bytes
import json
import re


router = APIRouter(prefix="/recipes", tags=["Recipes"])


class RecipeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    rating: float = Field(..., ge=0, le=5)
    image: str = Field(..., description="Image URL or identifier")
    ingredients: List[str] = Field(..., min_items=1)
    instructions: List[str] = Field(
        ..., min_items=1, description="Step-by-step instructions"
    )


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    rating: Optional[float] = Field(None, ge=0, le=5)
    image: Optional[str] = Field(None, description="Image URL or identifier")
    ingredients: Optional[List[str]] = None
    instructions: Optional[List[str]] = None


class RecipeOut(RecipeBase):
    id: str


def _to_recipe_out(doc: dict) -> RecipeOut:
    return RecipeOut(
        id=str(doc.get("_id")),
        name=doc.get("name"),
        rating=doc.get("rating"),
        image=doc.get("image"),
        ingredients=doc.get("ingredients", []),
        instructions=doc.get("instructions", []),
    )


def _parse_object_id(oid_str: str):
    try:
        from bson import ObjectId  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="bson is required. Install pymongo."
        ) from e
    try:
        return ObjectId(oid_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recipe id")


@router.post("/", response_model=RecipeOut, status_code=201)
def create_recipe(payload: RecipeCreate):
    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    doc = payload.dict()
    result = col.insert_one(doc)
    inserted = col.find_one({"_id": result.inserted_id})
    return _to_recipe_out(inserted)


@router.post("/with-image", response_model=RecipeOut, status_code=201)
async def create_recipe_with_image(
    name: str = Form(...),
    rating: float = Form(...),
    ingredients: List[str] = Form(..., description="JSON array of strings"),
    instructions: List[str] = Form(..., description="JSON array of strings"),
    image: UploadFile = File(...),
):
    # Parse list fields
    try:
        
        if not isinstance(ingredients, list) or not all(
            isinstance(i, str) for i in ingredients
        ):
            raise ValueError("ingredients must be a JSON array of strings")
        if not isinstance(instructions, list) or not all(
            isinstance(i, str) for i in instructions
        ):
            raise ValueError("instructions must be a JSON array of strings")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid list payloads: {e}"
        )

    # Upload image to Cloudinary
    try:
        file_bytes = await image.read()
        image_url = upload_image_bytes(
            file_bytes, original_filename=image.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Persist recipe
    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    doc = {
        "name": name,
        "rating": float(rating),
        "image": image_url,  # public Cloudinary URL
        "ingredients": ingredients,
        "instructions": instructions,
    }

    result = col.insert_one(doc)
    inserted = col.find_one({"_id": result.inserted_id})
    return _to_recipe_out(inserted)


@router.get("/", response_model=List[RecipeOut])
def list_recipes():
    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    items = [_to_recipe_out(doc) for doc in col.find().sort("_id", -1)]
    return items


@router.get("/search", response_model=List[RecipeOut])
def search_recipes(
    ingredient: Optional[str] = None,
    ingredients: Optional[List[str]] = Query(
        None,
        description="Repeat param for multiple: ingredients=tomato&ingredients=onion",
    ),
    mode: str = Query(
        "any",
        regex="^(any|all)$",
        description="Match recipes containing any or all of the ingredients",
    ),
    skip: int = 0,
    limit: int = 20,
):
    """Search recipes by one or many ingredients (case-insensitive substring).

    - Provide `ingredient` for a single term, or repeat `ingredients` for multiple term.
    - `mode=any` (default) matches if any term is present; `mode=all` requires all term.
    """
    # Normalize terms
    terms: List[str] = []
    if ingredients:
        terms.extend([t.strip() for t in ingredients if t and t.strip()])
    if ingredient and ingredient.strip():
        terms.append(ingredient.strip())
    # Deduplicate while preserving order
    seen = set()
    terms = [t for t in terms if not (t in seen or seen.add(t))]

    if not terms:
        raise HTTPException(
            status_code=400,
            detail="Provide ingredient or ingredients query param",
        )

    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # Build case-insensitive substring regex filters for each term
    regex_filters = [
        {
            "ingredients": {
                "$elemMatch": {"$regex": re.escape(t), "$options": "i"}
            }
        }
        for t in terms
    ]

    if mode == "all":
        mongo_query = {"$and": regex_filters}
    else:  # any
        mongo_query = {"$or": regex_filters}

    cursor = (
        col.find(mongo_query)
        .skip(max(0, int(skip)))
        .limit(max(1, min(100, int(limit))))
    )

    return [_to_recipe_out(doc) for doc in cursor]


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: str):
    oid = _parse_object_id(recipe_id)

    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    doc = col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _to_recipe_out(doc)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: str, payload: RecipeUpdate):
    oid = _parse_object_id(recipe_id)

    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    res = col.find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=True,
    )
    if not res:
        raise HTTPException(status_code=404, detail="Recipe not found")
    # Some pymongo versions require a second fetch for return_document; ensure doc
    doc = col.find_one({"_id": oid})
    return _to_recipe_out(doc)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: str):
    oid = _parse_object_id(recipe_id)

    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    res = col.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return None
