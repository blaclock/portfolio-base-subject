from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user_id
from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostResponse
from app.schemas.user import UserProfileResponse, UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/{username}")
def get_user_profile(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )

    followers_count = (
        db.query(func.count(Follow.id)).filter(Follow.following_id == user.id).scalar()
    )
    following_count = (
        db.query(func.count(Follow.id)).filter(Follow.follower_id == user.id).scalar()
    )
    is_following = (
        db.query(Follow)
        .filter(Follow.follower_id == current_user_id, Follow.following_id == user.id)
        .first()
        is not None
    )

    return {
        "data": UserProfileResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            followers_count=followers_count,
            following_count=following_count,
            is_following=is_following,
        ).model_dump()
    }


@router.get("/{username}/posts")
def get_user_posts(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )

    posts = (
        db.query(Post)
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for post in posts:
        like_count = (
            db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
        )
        is_liked = (
            db.query(Like)
            .filter(Like.post_id == post.id, Like.user_id == current_user_id)
            .first()
            is not None
        )
        result.append(
            PostResponse(
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
        )

    return {"data": result}


@router.post("/{username}/follow", status_code=201)
def follow_user(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )
    if target.id == current_user_id:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": "自分自身をフォローすることはできません"},
        )
    existing = (
        db.query(Follow)
        .filter(Follow.follower_id == current_user_id, Follow.following_id == target.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail={"code": "ALREADY_FOLLOWING", "message": "既にフォローしています"},
        )

    follow = Follow(follower_id=current_user_id, following_id=target.id)
    db.add(follow)
    db.commit()
    return {"data": {"message": "フォローしました"}}


@router.delete("/{username}/follow")
def unfollow_user(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )
    follow = (
        db.query(Follow)
        .filter(Follow.follower_id == current_user_id, Follow.following_id == target.id)
        .first()
    )
    if not follow:
        raise HTTPException(
            status_code=400,
            detail={"code": "NOT_FOLLOWING", "message": "フォローしていません"},
        )
    db.delete(follow)
    db.commit()
    return {"data": {"message": "フォローを解除しました"}}


@router.get("/{username}/followers")
def get_followers(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )
    follower_ids = (
        db.query(Follow.follower_id)
        .filter(Follow.following_id == user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    followers = (
        db.query(User).filter(User.id.in_([fid for (fid,) in follower_ids])).all()
    )
    return {
        "data": [UserResponse.model_validate(f).model_dump() for f in followers]
    }


@router.get("/{username}/following")
def get_following(
    username: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ユーザが見つかりません"},
        )
    following_ids = (
        db.query(Follow.following_id)
        .filter(Follow.follower_id == user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    followings = (
        db.query(User).filter(User.id.in_([fid for (fid,) in following_ids])).all()
    )
    return {
        "data": [UserResponse.model_validate(f).model_dump() for f in followings]
    }
