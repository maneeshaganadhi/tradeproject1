import traceback
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

from ai_model import predict_value
from routers import analyze

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register router
app.include_router(analyze.router)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT settings
SECRET_KEY = "my_secure_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authentication dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# -------------------------------
# Pydantic Schemas
# -------------------------------

class UserCreate(BaseModel):
    username: str
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters")
        return v


class TradeSchema(BaseModel):
    topic: str


# -------------------------------
# Authentication APIs
# -------------------------------

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(user.password)

    new_user = models.User(
        username=user.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------------
# Basic API
# -------------------------------

@app.get("/")
def home():
    return {"message": "Trade Project API Running"}


# -------------------------------
# CRUD APIs
# -------------------------------

@app.post("/trade-opportunities")
def create_trade(
    trade: TradeSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    new_trade = models.Trade(topic=trade.topic)

    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)

    return new_trade


@app.put("/trade-opportunities/{trade_id}")
def update_trade(
    trade_id: int,
    trade: TradeSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    db_trade.topic = trade.topic

    db.commit()
    db.refresh(db_trade)

    return db_trade


@app.delete("/trade-opportunities/{trade_id}")
def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    db.delete(db_trade)
    db.commit()

    return {"message": "Trade deleted successfully"}


# -------------------------------
# AI APIs
# -------------------------------

@app.post("/ai-analysis")
def ai_analysis(value: int):
    result = predict_value(value)
    return {"prediction": result}


@app.get("/trade-ai-analysis")
def trade_analysis(db: Session = Depends(get_db)):

    trades = db.query(models.Trade).all()
    total = len(trades)

    if total == 0:
        comment = "No trade opportunities available"
    elif total < 5:
        comment = "Few opportunities found. Market growing."
    else:
        comment = "Strong market with many opportunities"

    return {
        "total_trades": total,
        "ai_comment": comment
    }