from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user_id
from app.models.like import Like
from app.models.post import Post

router = APIRouter(prefix="/api/v1/posts", tags=["likes"])


@router.post("/{post_id}/like", status_code=201)
def like_post(
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
    if post.user_id == current_user_id:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": "自分の投稿にはいいねできません"},
        )
    existing = (
        db.query(Like)
        .filter(Like.user_id == current_user_id, Like.post_id == post_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail={"code": "ALREADY_LIKED", "message": "既にいいねしています"},
        )

    like = Like(user_id=current_user_id, post_id=post_id)
    db.add(like)
    db.commit()

    like_count = (
        db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    )
    return {"data": {"message": "いいねしました", "like_count": like_count}}


@router.delete("/{post_id}/like")
def unlike_post(
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
    like = (
        db.query(Like)
        .filter(Like.user_id == current_user_id, Like.post_id == post_id)
        .first()
    )
    if not like:
        raise HTTPException(
            status_code=400,
            detail={"code": "NOT_LIKED", "message": "いいねしていません"},
        )
    db.delete(like)
    db.commit()

    like_count = (
        db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    )
    return {"data": {"message": "いいねを解除しました", "like_count": like_count}}
