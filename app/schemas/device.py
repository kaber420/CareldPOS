from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.device import DeviceType, DeviceStatus


class CustomerResponse(BaseModel):
    """Schema de respuesta de cliente (simplificada)"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: str
    email: Optional[str] = None


class DeviceBase(BaseModel):
    """Schema base de dispositivo"""
    brand: str
    model: str
    serial_number: Optional[str] = None
    imei: Optional[str] = None
    device_type: DeviceType = DeviceType.SMARTPHONE
    color: Optional[str] = None
    storage: Optional[str] = None
    password_pattern: Optional[str] = None
    accessories: Optional[str] = None


class DeviceCreate(DeviceBase):
    """Schema para crear dispositivo"""
    customer_id: int


class DeviceUpdate(BaseModel):
    """Schema para actualizar dispositivo"""
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    imei: Optional[str] = None
    device_type: Optional[DeviceType] = None
    color: Optional[str] = None
    storage: Optional[str] = None
    password_pattern: Optional[str] = None
    accessories: Optional[str] = None
    status: Optional[DeviceStatus] = None


class DeviceResponse(DeviceBase):
    """Schema de respuesta de dispositivo"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer: Optional[CustomerResponse] = None
    status: DeviceStatus
    created_at: datetime
    updated_at: datetime
    photos: Optional[str] = None
    
    @classmethod
    def model_validate(cls, obj):
        """Sobrescribir para convertir nombres de archivo en URLs"""
        data = super().model_validate(obj)
        if data.photos:
            # Convertir nombres de archivo en URLs completas
            photo_names = [p.strip() for p in data.photos.split(',')]
            data.photos = ','.join([
                f'/api/v1/uploads/photo/{name}' if not name.startswith('/api/') else name
                for name in photo_names if name
            ])
        return data
