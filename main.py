from fastapi import FastAPI
from routes.admin_post_route import router as admin_post_router
from routes.admin_request_route import router as admin_request_router

app = FastAPI(title="Admin Authentication API")

app.include_router(admin_post_router)
app.include_router(admin_request_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Admin Authentication API"}
