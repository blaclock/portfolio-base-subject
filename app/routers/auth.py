from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import generate_token, get_current_user_id
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    UserDetailResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", status_code=201)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(
            status_code=400,
            detail={"code": "USERNAME_EXISTS", "message": "このユーザ名は既に使用されています"},
        )
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=400,
            detail={"code": "EMAIL_EXISTS", "message": "このメールアドレスは既に使用されています"},
        )

    user = User(
        username=req.username,
        email=req.email,
        password_hash=pwd_context.hash(req.password),
        display_name=req.display_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token(user.id, user.username)
    return {
        "data": AuthResponse(
            token=token,
            user=UserResponse.model_validate(user),
        ).model_dump()
    }


@router.post("/login")
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "メールアドレスまたはパスワードが正しくありません",
            },
        )

    token = generate_token(user.id, user.username)
    return {
        "data": AuthResponse(
            token=token,
            user=UserResponse.model_validate(user),
        ).model_dump()
    }


@router.get("/me")
def get_me(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )
    return {"data": UserDetailResponse.model_validate(user).model_dump()}
