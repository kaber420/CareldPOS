from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, UserRole
from app.models.setting import Setting
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

class SettingUpdate(BaseModel):
    value: str

class PublicSetting(BaseModel):
    key: str
    value: str

@router.get("/", response_model=List[Setting])
def get_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar todas las configuraciones (Solo Admin)"""
    print(f"🔍 GET /settings requested by user: {current_user.username}")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return session.exec(select(Setting)).all()

@router.get("/public", response_model=List[PublicSetting])
def get_public_settings(session: Session = Depends(get_session)):
    """Obtener configuraciones marcadas como públicas"""
    settings = session.exec(select(Setting).where(Setting.is_public == True)).all()
    return settings

@router.put("/key/{key}", response_model=Setting)
def update_setting(
    key: str,
    setting_update: SettingUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Actualizar una configuración específica (Solo Admin)"""
    print(f"🔄 PUT /settings/key/{key} requested by user: {current_user.username}")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    setting = session.exec(select(Setting).where(Setting.key == key)).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración '{key}' no encontrada"
        )
    
    setting.value = setting_update.value
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting

def seed_settings(session: Session):
    """Sembrar configuraciones iniciales si no existen"""
    defaults = [
        {
            "key": "portal_url",
            "value": "",
            "description": "URL base para el portal de clientes (dejar vacío para usar el mismo dominio)",
            "type": "string",
            "is_public": True
        },
        {
            "key": "store_name",
            "value": "CareldPOS",
            "description": "Nombre de la tienda mostrado en los tickets",
            "type": "string",
            "is_public": True
        },
        {
            "key": "ticket_footer",
            "value": "Conserve este ticket para recoger su equipo.",
            "description": "Texto al pie del ticket",
            "type": "string",
            "is_public": True
        }
    ]

    for d in defaults:
        existing = session.exec(select(Setting).where(Setting.key == d["key"])).first()
        if not existing:
            setting = Setting(**d)
            session.add(setting)
    
    session.commit()
