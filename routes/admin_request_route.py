from fastapi import APIRouter, HTTPException
from models.admin import Admin
from services.admin_request_service import login_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login")
async def login(admin: Admin):
    response = await login_admin(admin)

    if "error" in response:
        raise HTTPException(status_code=401, detail=response["error"])
    
    return response