from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user_id
from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreateRequest, PostResponse, PostUpdateRequest

router = APIRouter(prefix="/api/v1", tags=["posts"])


def _post_to_response(post: Post, current_user_id: int, db: Session) -> dict:
    user = db.query(User).filter(User.id == post.user_id).first()
    like_count = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
    is_liked = (
        db.query(Like)
        .filter(Like.post_id == post.id, Like.user_id == current_user_id)
        .first()
        is not None
    )
    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        content=post.content,
        username=user.username,
        display_name=user.display_name,
        like_count=like_count,
        is_liked=is_liked,
        created_at=post.created_at,
        updated_at=post.updated_at,
    ).model_dump()


@router.post("/posts", status_code=201)
def create_post(
    req: PostCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    post = Post(user_id=current_user_id, content=req.content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"data": _post_to_response(post, current_user_id, db)}


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "投稿が見つかりません"},
        )
    return {"data": _post_to_response(post, current_user_id, db)}


@router.put("/posts/{post_id}")
def update_post(
    post_id: int,
    req: PostUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "投稿が見つかりません"},
        )
    if post.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "この投稿を編集する権限がありません"},
        )
    post.content = req.content
    db.commit()
    db.refresh(post)
    return {"data": _post_to_response(post, current_user_id, db)}


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "投稿が見つかりません"},
        )
    if post.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "この投稿を削除する権限がありません"},
        )
    db.delete(post)
    db.commit()
    return {"data": {"message": "投稿を削除しました"}}


@router.get("/timeline")
def get_timeline(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
    filter: str = Query(default="all"),
):
    query = db.query(Post)
    if filter == "following":
        following_ids = (
            db.query(Follow.following_id)
            .filter(Follow.follower_id == current_user_id)
            .subquery()
        )
        query = query.filter(
            (Post.user_id.in_(following_ids)) | (Post.user_id == current_user_id)
        )
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    return {"data": [_post_to_response(p, current_user_id, db) for p in posts]}
