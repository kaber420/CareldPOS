from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


@router.get("/me", response_model=UserResponse, tags=["Perfil"])
def read_users_me(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user


@router.put("/me", response_model=UserResponse, tags=["Perfil"])
def update_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualizar perfil del usuario actual"""
    update_data = user_data.model_dump(exclude_unset=True)

    if "username" in update_data:
        # Verificar que el nuevo username no esté en uso
        existing = session.exec(
            select(User).where(User.username == update_data["username"])
        ).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        current_user.username = update_data["username"]

    if "email" in update_data:
        existing = session.exec(
            select(User).where(User.email == update_data["email"])
        ).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = update_data["email"]

    if "full_name" in update_data:
        current_user.full_name = update_data["full_name"]

    if "phone" in update_data:
        current_user.phone = update_data["phone"]

    if "password" in update_data and update_data["password"]:
        current_user.hashed_password = User.hash_password(update_data["password"])

    if "is_active" in update_data:
        # Solo admin puede desactivar usuarios
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can activate/deactivate users"
            )
        current_user.is_active = update_data["is_active"]

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/", response_model=List[UserResponse], tags=["Usuarios"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """Listar todos los usuarios (solo admin)"""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserResponse, tags=["Usuarios"])
def read_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """Obtener usuario por ID (solo admin)"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse, tags=["Usuarios"])
def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """Actualizar usuario por ID (solo admin)"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            if field == "password":
                setattr(user, "hashed_password", User.hash_password(value))
            else:
                setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", tags=["Usuarios"])
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """Eliminar usuario (solo admin)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
