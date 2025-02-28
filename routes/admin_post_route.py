from fastapi import APIRouter, HTTPException
from models.admin import Admin
from services.admin_post_service import register_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/register")
async def register(admin: Admin):
    response = await register_admin(admin)
    
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    
    return response
