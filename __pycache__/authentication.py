#pip install "pwdlib[argon2]" pyjwt python-multipart

# The Mental Model: 4 Moving Parts
# A complete auth system consists of four pieces:

# Password Utilities: Hash passwords before storing them; verify raw passwords against the hash at login.

# Token Generation: Encode user identity (sub) and expiration time (exp) into a cryptographically signed JWT.

# Login Endpoint (/token): Validates credentials and returns the access token.

# Auth Dependency (get_current_user): Decodes the token from incoming requests and protects routes using FastAPI's dependency injection.

from datetime import datetime,timedata,timezone
from typing import Annotated
import jwt
from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pwd import passwordHash
from pydantic import BaseModel

app=FastAPI()
SECRET_KEY="your-secure-secret-key-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Password hasher using modern Argon2
pwd_context = PasswordHash.recommended()

# OAuth2 scheme: tells Swagger UI and FastAPI where clients get tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str


class UserPublic(BaseModel):
    username: str
    email: str

fake_users_db = {
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        # Pre-hashed password for "secret123"
        "hashed_password": pwd_context.hash("secret123"),
        "role": "admin",
    }
}
def verify_password(plain_password: str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- Reusable Auth Dependency ---
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the signature + expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


# --- Route 1: Login / Token Endpoint ---
@app.post("/token", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    # Issue JWT with username stored in the 'sub' (subject) claim
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Route 2: Protected Endpoint ---
@app.get("/users/me", response_model=UserPublic)
def read_current_user(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user


# --- Route 3: Role-Protected Endpoint ---
@app.get("/admin/dashboard")
def admin_only_data(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return {"status": "Welcome to the admin panel!"}