from fastapi import APIRouter, Depends, HTTPException, status

from .. import auth
from ..models import User
from ..schemas import UserCreate, UserRead

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate) -> UserRead:
    # is the user already in the database?
    if await User.exists(email=user.email):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    # create the user
    user_data = user.dict(exclude_unset=True)
    user_data["password"] = auth.hash_password(user_data["password"])
    new_user = await User.create(**user_data)
    return await UserRead.from_tortoise_orm(new_user)


@router.get("/", response_model=list[UserRead])
async def read_users(_=Depends(auth.get_current_user)) -> list[UserRead]:
    return await UserRead.from_queryset(User.all())


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, _=Depends(auth.get_current_user)) -> UserRead:
    return await UserRead.from_queryset_single(User.get(id=user_id))
