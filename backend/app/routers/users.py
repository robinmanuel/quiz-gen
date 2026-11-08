from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.dependencies import get_current_user
from app.security import verify_password, get_password_hash


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Password change requires current_password verification
    if payload.new_password:
        if not payload.current_password:
            raise HTTPException(
                status_code=400,
                detail="current_password is required to set a new password",
            )
        if not verify_password(payload.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        current_user.hashed_password = get_password_hash(payload.new_password)

    if payload.email and payload.email != current_user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = payload.email

    if payload.username and payload.username != current_user.username:
        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = payload.username

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.delete(current_user)
    db.commit()
    return None

