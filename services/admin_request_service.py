from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from databases.mongodb import get_database
from databases.redis import get_client
from models.admin import Admin
import json

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "markmarkmark"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Get Database and Redis Clients
db = get_database()
admin_collection = db["credentials"]
login_logs_collection = db["login_logs"]
redis_client = get_client()

async def get_admin_by_username(username: str):
    return await admin_collection.find_one({"username": username})

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(username: str, expires_delta: timedelta = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def login_admin(admin: Admin):
    db_admin = await get_admin_by_username(admin.username)
    
    if not db_admin or not await verify_password(admin.password, db_admin["password"]):
        login_log = {
            "username": admin.username,
            "login_time": datetime.utcnow(),
            "status": "Failed"
        }
        await login_logs_collection.insert_one(login_log)
        return {"error": "Invalid username or password"}

    access_token = await create_access_token(db_admin["username"])

    redis_client.rpush("login_attempts", json.dumps({
        "username": admin.username,
        "timestamp": str(datetime.utcnow()),
        "status": "Success"
    }))

    login_log = {
        "username": db_admin["username"],
        "login_time": datetime.utcnow(),
        "status": "Success"
    }
    await login_logs_collection.insert_one(login_log)

    return {
        "message": "Login Successful",
        "access_token": access_token,
        "token_type": "bearer"
    }
