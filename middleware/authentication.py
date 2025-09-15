from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

TOKENS = [
    "dev-ranpo",
    "more-token",
]


async def authenticate(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials.credentials in TOKENS:
        return True
    raise HTTPException(status_code=401, detail="Invalid token")
