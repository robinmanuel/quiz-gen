from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenPair,
)
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_token,
    revoke_token,
    is_token_revoked,
)
from app.dependencies import get_current_user, oauth2_scheme

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", response_model=TokenPair)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
def refresh_tokens(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    if is_token_revoked(payload.refresh_token):
        raise invalid_exc
    try:
        data = decode_token(payload.refresh_token)
    except JWTError:
        raise invalid_exc

    if data.get("type") != "refresh":
        raise invalid_exc

    username: str = data.get("sub")
    if not username or not db.query(User).filter(User.username == username).first():
        raise invalid_exc

    # Revoke the used refresh token (rotation)
    revoke_token(payload.refresh_token)

    new_access = create_access_token(data={"sub": username})
    new_refresh = create_refresh_token(data={"sub": username})
    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=204)
def logout(
    payload: RefreshRequest | None = None,
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
):
    """Revoke the current access token and optional refresh token."""
    revoke_token(token)
    if payload and payload.refresh_token:
        revoke_token(payload.refresh_token)
    return None


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Initiate password recovery. Returns a short-lived reset token if the user exists."""
    user = db.query(User).filter(User.email == payload.email).first()
    reset_token = create_password_reset_token(user.email) if user else None
    return ForgotPasswordResponse(
        message="If an account with that email exists, a password reset token has been generated.",
        reset_token=reset_token,
    )


@router.post("/reset-password", status_code=200)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset a user's password using a valid password reset token."""
    invalid_exc = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired password reset token",
    )
    if is_token_revoked(payload.reset_token):
        raise invalid_exc
    try:
        data = decode_token(payload.reset_token)
    except JWTError:
        raise invalid_exc

    if data.get("type") != "password_reset":
        raise invalid_exc

    email: str = data.get("sub")
    user = db.query(User).filter(User.email == email).first() if email else None
    if not user:
        raise invalid_exc

    user.hashed_password = get_password_hash(payload.new_password)
    revoke_token(payload.reset_token)
    db.commit()
    return {"message": "Password has been reset successfully"}


