from fastapi import APIRouter, Depends, HTTPException, status

from .. import auth
from ..models import User
from ..schemas import UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=UserRead)
async def read_me(current_user: User = Depends(auth.get_current_user)) -> UserRead:
    return await UserRead.from_queryset_single(User.get(id=current_user.id))


@router.put("/", response_model=UserRead)
async def update_me(
    user: UserUpdate,
    current_user: User = Depends(auth.get_current_user),
) -> UserRead:
    # is the requested email change allowed?
    if current_user.email != user.email and await User.exists(email=user.email):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    # update the user
    user_data = user.dict(exclude_unset=True)
    if "password" in user_data:
        user_data["password"] = auth.hash_password(user_data["password"])
    await User.filter(id=current_user.id).update(**user_data)
    return await UserRead.from_queryset_single(User.get(id=current_user.id))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: User = Depends(auth.get_current_user)):
    await current_user.delete()
