from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth_schema import (
    UserRegister, UserLogin, TokenResponse,
    RefreshRequest, UserResponse, UserOrgsResponse,
)
from app.services.auth_service import (
    register_user, login_user, refresh_tokens,
    get_user_organizations, add_user_to_org,
)
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db, data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


# OAuth2 form-compatible login (for Swagger UI "Authorize" button)
@router.post("/token", response_model=TokenResponse, include_in_schema=False)
def token(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        return login_user(db, form.username, form.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        return refresh_tokens(db, data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_active_user)):
    return user


@router.get("/me/organizations", response_model=list[UserOrgsResponse])
def my_organizations(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return get_user_organizations(db, user.id)


@router.post("/me/organizations/{organization_id}", status_code=201)
def join_organization(
    organization_id: int,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        add_user_to_org(db, user.id, organization_id)
        return {"message": "Joined organization successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
