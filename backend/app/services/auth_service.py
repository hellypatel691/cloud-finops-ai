from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User, OrganizationMember
from app.models.organization import Organization
from app.schemas.auth_schema import UserRegister
from app.utils.auth import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.logger import get_logger

logger = get_logger(__name__)


def register_user(db: Session, data: UserRegister) -> User:
    user = User(
        email           = data.email.lower().strip(),
        hashed_password = hash_password(data.password),
        full_name       = data.full_name,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Registered new user: %s", user.email)
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("A user with this email already exists.")


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email.lower().strip()).first()

    if user is None or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password.")

    if not user.is_active:
        raise ValueError("Account is disabled.")

    access_token  = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    logger.info("User logged in: %s", user.email)
    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
    }


def refresh_tokens(db: Session, refresh_token: str) -> dict:
    from app.utils.auth import decode_token
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type.")

    user_id = payload.get("sub")
    user    = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or not user.is_active:
        raise ValueError("User not found.")

    access_token  = create_access_token({"sub": str(user.id)})
    new_refresh   = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token":  access_token,
        "refresh_token": new_refresh,
        "token_type":    "bearer",
    }


def get_user_organizations(db: Session, user_id: int) -> list[dict]:
    memberships = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == user_id)
        .all()
    )
    result = []
    for m in memberships:
        org = db.query(Organization).filter(Organization.id == m.organization_id).first()
        if org:
            result.append({"id": org.id, "name": org.name, "role": m.role})
    return result


def add_user_to_org(
    db: Session,
    user_id: int,
    organization_id: int,
    role: str = "member",
) -> OrganizationMember:
    existing = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
        )
        .first()
    )
    if existing:
        return existing

    member = OrganizationMember(
        user_id         = user_id,
        organization_id = organization_id,
        role            = role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
