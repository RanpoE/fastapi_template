from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from inference_sdk import InferenceHTTPClient
import json
import os
from uuid import uuid4
from middleware.authentication import authenticate


router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate)])
async def basic():
    try:
        return {"message": "Authorized access."}
    except Exception as e:
        raise HTTPException(e)


@router.post("/upload-v2")
async def handle_flow_upload(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{uuid4().hex}_{os.path.basename(file.filename)}"
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())

        with open("data.json") as f:
            constants = json.load(f)

        api_url = os.environ.get(
            "ROBOFLOW_API_URL", "https://serverless.roboflow.com"
        )
        api_key = os.environ.get("ROBOFLOW_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, detail="ROBOFLOW_API_KEY is not set"
            )

        client = InferenceHTTPClient(api_url=api_url, api_key=api_key)

        result = client.run_workflow(
            workspace_name="devml",
            workflow_id="small-object-detection-sahi-2",
            images={"image": filepath},
            use_cache=True,
        )

        predictions = result[0].get("predictions")

        print(predictions, "ML predictions")

        best_ingredients = {}

        # Step 2: Loop through predictions
        for v in predictions.get("predictions", []):
            class_name = constants.get(v["class"])
            confidence = v["confidence"]

            # Step 3: Keep only the highest confidence for each class
            if class_name != "undefined" and (
                class_name not in best_ingredients
                or confidence > best_ingredients[class_name]
            ):
                best_ingredients[class_name] = confidence

        # Step 4: Extract just the unique class names
        upload = os.environ.get("UPLOAD_IMAGES", "")
        if upload.lower() == "true":
            ingredients = set(best_ingredients.keys())

            category = (
                "_".join(sorted(ingredients)) if ingredients else "unknown"
            )

            new_path = os.path.join(upload_dir, category)
            os.makedirs(new_path, exist_ok=True)

            final_filepath = os.path.join(new_path, filename)
            os.rename(filepath, final_filepath)
        else:
            os.remove(filepath)

        return best_ingredients
    except Exception as e:
        print(f"Error -> {e}")
        raise HTTPException(e)
