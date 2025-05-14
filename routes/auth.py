from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from config.db import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin
from utils.auth import hash_password
from sqlalchemy.exc import IntegrityError
from utils.geolocation import get_coordinates_from_address
from utils.auth import verify_password
from utils.jwt import create_access_token

auth = APIRouter(tags=["Auth"], prefix="/auth")

@auth.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pwd = hash_password(user.password)

    lat, lng = get_coordinates_from_address(user.address)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
        role=user.role,
        address=user.address,
        phone=user.phone,
        latitude=lat,
        longitude=lng,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error saving user")

    return {
        "message": "User registered successfully",
        "guid": new_user.guid
    }


@auth.post("/signin", response_model=dict, description="User login and token generation")
def signin(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": user.guid, "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "guid": user.guid,
        "role": user.role
    }