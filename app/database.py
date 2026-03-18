from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Solo muestra SQL si DEBUG es True
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """Crear tablas de la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency para obtener sesión de BD"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


# Factory de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
