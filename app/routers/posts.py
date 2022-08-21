from fastapi import APIRouter, Depends, HTTPException, status

from .. import auth
from ..models import Post, User
from ..schemas import PostCreate, PostRead, PostUpdate

router = APIRouter()


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate, current_user: User = Depends(auth.get_current_user)
) -> PostRead:
    # new_post = await Post.create(**post.dict(exclude_unset=True), author_id=current_user.id)
    new_post = await Post.create(**post.dict(exclude_unset=True), author=current_user)
    return await PostRead.from_tortoise_orm(new_post)


@router.get("/", response_model=list[PostRead])
async def read_posts(limit: int = 10, skip: int = 0, search: str = "") -> list[PostRead]:
    return await PostRead.from_queryset(
        Post.filter(title__icontains=search).all().offset(skip).limit(limit)
    )


@router.get("/{post_id}", response_model=PostRead)
async def read_post(post_id: int) -> PostRead:
    if db_post := await PostRead.from_queryset_single(Post.get(id=post_id)):
        return db_post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.put("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    post: PostUpdate,
    current_user: User = Depends(auth.get_current_user),
) -> PostRead:
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if current_user.id != db_post.author_id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    await Post.filter(id=post_id).update(**post.dict(exclude_unset=True))
    return await PostRead.from_queryset_single(Post.get(id=post_id))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, current_user: User = Depends(auth.get_current_user)):
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if current_user.id != db_post.author_id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    await Post.filter(id=post_id).delete()


@router.post("/{post_id}/upvote", status_code=status.HTTP_204_NO_CONTENT)
async def upvote_post(post_id: int, current_user: User = Depends(auth.get_current_user)):
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if current_user.id == db_post.author_id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    # user can only vote for a  post once
    if not await db_post.votes.filter(id=current_user.id).first():
        await db_post.votes.add(current_user)


@router.post("/{post_id}/downvote", status_code=status.HTTP_204_NO_CONTENT)
async def downvote_post(post_id: int, current_user: User = Depends(auth.get_current_user)):
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if current_user.id == db_post.author_id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    # user can only vote for a  post once
    if await db_post.votes.filter(id=current_user.id).first():
        await db_post.votes.remove(current_user)
