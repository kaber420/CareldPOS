from typing import Optional
from sqlmodel import Session, select
from app.models.user import User
from app.core.security import SecurityManager


class AuthService:
    """Servicio de autenticación y autorización"""

    def __init__(self, session: Session):
        self.session = session

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario con credenciales"""
        user = self.session.exec(
            select(User).where(User.username == username)
        ).first()

        if not user or not user.verify_password(password):
            return None

        if not user.is_active:
            return None

        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return self.session.exec(
            select(User).where(User.username == username)
        ).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.session.exec(
            select(User).where(User.email == email)
        ).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.session.get(User, user_id)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "receptionist",
        phone: Optional[str] = None
    ) -> User:
        """Crear nuevo usuario"""
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            phone=phone,
            hashed_password=User.hash_password(password)
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def user_exists(self, username: str, email: str) -> bool:
        """Verificar si usuario o email ya existen"""
        existing = self.session.exec(
            select(User).where(
                (User.username == username) | (User.email == email)
            )
        ).first()
        return existing is not None
