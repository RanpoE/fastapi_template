from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

TOKENS = [
    "your_token_1",
    "your_token_2",
    # Add more tokens as needed
]


async def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials in TOKENS:
        return True
    raise HTTPException(status_code=401, detail="Invalid token")
