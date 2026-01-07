FastAPI Template – Recipes Endpoint

Overview
- Adds MongoDB-backed CRUD for recipes at `/v1/recipes`.

Environment
- `MONGO_URI` (e.g., `mongodb://localhost:27017`)
- `MONGO_DB` (default: `appdb`)
- `MONGO_COLLECTION` (default: `recipes`)

Local Docker
- Build: `docker build -t fastapi-template .`
- Run: `docker run --env-file .env -p 8000:8000 fastapi-template`
- API will be available at `http://localhost:8000/`
- Ensure `.env` contains the environment variables above plus any optional Cloudinary/Roboflow keys.

Install Dependency
- `pip install pymongo` (MongoDB driver)
- `pip install cloudinary` (Cloudinary uploads)

API
- POST `/v1/recipes` – Create a recipe
- POST `/v1/recipes/with-image` – Create with multipart image
- GET `/v1/recipes` – List recipes
- GET `/v1/recipes/{id}` – Get one recipe
- PUT `/v1/recipes/{id}` – Update fields
- DELETE `/v1/recipes/{id}` – Remove recipe

Recipe schema
- name: string
- rating: number (0–5)
- image: string (URL, identifier, or stored file path)
- ingredients: string[]
- instructions: string[]

Create with image (multipart)
- Fields
  - `name`: text
  - `rating`: number
  - `ingredients`: JSON array of strings (e.g., `["flour","egg"]`)
  - `instructions`: JSON array of strings (e.g., `["Mix","Cook"]`)
  - `image`: file upload
  
Example (curl)
```
curl -X POST http://localhost:8000/v1/recipes/with-image \
  -F "name=Pancakes" \
  -F "rating=4.5" \
  -F 'ingredients=["flour","egg","milk"]' \
  -F 'instructions=["Mix","Cook","Serve"]' \
  -F "image=@/path/to/pancakes.jpg"
```

Cloudinary configuration
- Option 1: set `CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>`
- Option 2: set all of the following:
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`

The API stores the returned `secure_url` in the `image` field.

Storage note
- Recipe image uploads do not write to local disk; files are uploaded directly to Cloudinary and only the public URL is stored.

Deploying on Render
- Option A: Click-to-deploy with blueprint
  - Push this repo to GitHub (ensure `.env` is not committed; `.gitignore` now ignores it).
  - In Render, New → Blueprint, point to this repo/branch.
  - Render uses `render.yaml` to create a Python Web Service with:
    - Build: `pip install -r requirements.server.txt`
    - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Set environment variables in the service:
    - `MONGO_URI` (MongoDB Atlas connection string)
    - `MONGO_DB` (default `appdb`)
    - `MONGO_COLLECTION` (default `recipes`)
    - `CLOUDINARY_URL` or `CLOUDINARY_{CLOUD_NAME,API_KEY,API_SECRET}`
    - `ROBOFLOW_API_KEY` (required for `/v1/upload-v2`)
    - Optional: `ROBOFLOW_API_URL` (default `https://serverless.roboflow.com`)
    - Optional: `UPLOAD_IMAGES` (`true` to keep categorized copies in `uploads/` — note this is ephemeral on Render unless you add a disk)
  - Deploy. Health check path is `/`.

- Option B: Manual service (no blueprint)
  - New → Web Service → Connect repo → Environment: `Python`.
  - Build command: `pip install -r requirements.server.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Add the same environment variables as above.
  - Deploy.

Notes for Render
- MongoDB: Use MongoDB Atlas (free tier works) and paste the connection string into `MONGO_URI`.
- Secrets: Keep secrets in Render env vars; do not commit `.env`.
- Roboflow: `POST /v1/upload-v2` uses the serverless Roboflow workflow. If you want to move the API key to an env var, I can update the code to read `ROBOFLOW_API_KEY` instead of a hardcoded value.
- Disk: The `uploads/` folder is fine for temporary files. It resets on deploy/restart unless you attach a persistent disk.
