import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from prometheus_fastapi_instrumentator import Instrumentator
import os

try:
    import bcrypt
    if not hasattr(bcrypt, '__about__'):
        bcrypt.__about__ = type('about', (), {'__version__': bcrypt.__version__})()
except Exception:
    pass

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey1234567890abcdef")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="Auth Service", version="1.0.0")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

fake_db: dict[str, dict] = {}

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class UserInfo(BaseModel):
    username: str
    email: str
    created_at: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in fake_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

@app.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest):
    if body.username in fake_db:
        raise HTTPException(status_code=409, detail="Username already exists")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    fake_db[body.username] = {
        "password": hash_password(body.password),
        "email": body.email,
        "created_at": datetime.utcnow().isoformat(),
    }
    token = create_token({"sub": body.username})
    return TokenResponse(access_token=token, username=body.username)

@app.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = fake_db.get(body.username)
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token({"sub": body.username})
    return TokenResponse(access_token=token, username=body.username)

@app.get("/me", response_model=UserInfo)
def me(username: str = Depends(get_current_user)):
    user = fake_db[username]
    return UserInfo(username=username, email=user["email"], created_at=user["created_at"])

@app.post("/logout")
def logout(username: str = Depends(get_current_user)):
    return {"message": f"User '{username}' logged out successfully"}

@app.get("/verify")
def verify_token(username: str = Depends(get_current_user)):
    return {"valid": True, "username": username}
