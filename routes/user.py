from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import get_db
from schemas.user import UserResponse, UserUpdate
from models.user import User
from dependencies.auth import get_current_user

user = APIRouter(tags=["Users"], prefix="/user")

@user.get("/{guid}", response_model=UserResponse)
def get_user_by_guid(guid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.guid == guid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# UPDATE current user (token-based)
@user.put("/", response_model=dict)
def update_user(data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for key, value in data.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    return {"message": "User updated successfully"}

# DELETE current user (token-based)
@user.delete("/", response_model=dict)
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}