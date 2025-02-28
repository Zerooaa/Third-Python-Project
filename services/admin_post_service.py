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
redis_client = get_client()

async def get_admin_by_username(username: str):
    return await admin_collection.find_one({"username": username})

async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def register_admin(admin: Admin):
    existing_admin = await get_admin_by_username(admin.username)
    if existing_admin:
        return {"error": "Username already exists"}

    # Get the latest admin_id and increment
    latest_admin = await admin_collection.find_one(sort=[("admin_id", -1)])
    new_admin_id = (latest_admin.get("admin_id", 0) + 1) if latest_admin else 1

    # Hash the password before storing
    hashed_pwd = await hash_password(admin.password)
    
    # Create new admin data
    new_admin = {
        "admin_id": new_admin_id,
        "username": admin.username,
        "password": hashed_pwd,
        "role": "admin"  # Automatically assign "admin" role
    }

    # Store the request in Redis (Queue system)
    redis_client.rpush("admin_queue", json.dumps(new_admin))

    # Fetch the request from Redis and insert it into MongoDB
    stored_admin = redis_client.lpop("admin_queue")
    if stored_admin:
        stored_admin = json.loads(stored_admin)
        await admin_collection.insert_one(stored_admin)

    # Generate access token
    access_token = await create_access_token(data={"sub": admin.username})
    
    return {
        "message": "Admin Registered Successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }
