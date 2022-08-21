from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import auth
from ..schemas import Token
from ..settings import settings

router = APIRouter()


@router.post("/", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    if not (user := await auth.authenticate_user(form_data.username, form_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"id": user.id}, expires_delta=access_token_expires  # type: ignore
    )
    return {"access_token": access_token, "token_type": "bearer"}
