import os
from datetime import datetime,timedelta,timezone
import bcrypt
from jose import jwt,JWTError

SECRET_KEY=os.getenv("MOODIFY_SECRET_KEY","change-this-in-production")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

def hash_password(password:str)->str:
    raw=password.encode("utf-8")
    if not raw: raise ValueError("Password cannot be empty.")
    if len(raw)>72: raise ValueError("Password cannot exceed 72 UTF-8 bytes.")
    return bcrypt.hashpw(raw,bcrypt.gensalt()).decode("utf-8")

def verify_password(password:str,hashed_password:str)->bool:
    try:
        raw=password.encode("utf-8")
        return len(raw)<=72 and bcrypt.checkpw(raw,hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(user_id:int)->str:
    exp=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub":str(user_id),"exp":exp},SECRET_KEY,algorithm=ALGORITHM)

def decode_access_token(token:str):
    try:
        sub=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM]).get("sub")
        return int(sub) if sub is not None else None
    except (JWTError,ValueError,TypeError): return None
