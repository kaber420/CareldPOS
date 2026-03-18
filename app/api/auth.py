from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, Token, UserRole
from app.schemas.user import UserCreate, TokenData
from app.core.security import SecurityManager
from app.core.dependencies import OAuth2Form, get_current_user

router = APIRouter()


@router.get("/status", tags=["Estado"])
def get_auth_status(session: Session = Depends(get_session)):
    """Verificar si el sistema necesita configuración inicial"""
    users = session.exec(select(User)).all()
    return {
        "needs_setup": len(users) == 0,
        "users_count": len(users)
    }


@router.post("/setup", response_model=User, tags=["Setup"])
def setup_initial(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Registro del primer usuario (solo funciona si no hay usuarios en el sistema).
    Solo para configuración inicial - DESACTIVADO cuando ya existe al menos un usuario.
    """
    # Verificar si ya existen usuarios
    existing_users = session.exec(select(User)).all()
    
    if len(existing_users) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Setup no disponible. Ya existen usuarios en el sistema."
        )
    
    # Crear primer usuario como admin
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=UserRole.ADMIN,  # Forzar rol admin para el primer usuario
        phone=user_data.phone,
        hashed_password=User.hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/register", response_model=User, tags=["Registro"])
def register(
    user_data: UserCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Registrar un nuevo usuario (solo admin puede crear usuarios)"""
    # Verificar que el usuario actual sea admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create new users"
        )
    
    # Verificar si el usuario ya existe
    existing = session.exec(
        select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Crear usuario
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        phone=user_data.phone,
        hashed_password=User.hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token, tags=["Autenticación"])
def login(
    form_data: OAuth2Form = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login de usuario.
    Usa OAuth2PasswordRequestForm (username/password en form-data)
    """
    # Verificar si hay usuarios en el sistema
    users = session.exec(select(User)).all()
    users_count = len(users)
    
    if users_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_USERS",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Crear tokens
    access_token = SecurityManager.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )

    refresh_token = SecurityManager.create_refresh_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token, tags=["Autenticación"])
def refresh_token(
    refresh_token: str,
    session: Session = Depends(get_session)
):
    """Refrescar token de acceso usando refresh token"""
    payload = SecurityManager.decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario existe y está activo
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear nuevo access token
    new_access_token = SecurityManager.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
