from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.repair import Repair


class DeviceType(str, Enum):
    """Tipos de dispositivo"""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    SMARTWATCH = "smartwatch"
    CONSOLE = "console"
    OTHER = "other"


class DeviceStatus(str, Enum):
    """Estado del dispositivo"""
    REGISTERED = "registered"      # Registrado en el sistema
    IN_REPAIR = "in_repair"        # En reparación
    WAITING_PARTS = "waiting_parts"  # Esperando repuestos
    READY = "ready"                # Listo para entrega
    DELIVERED = "delivered"        # Entregado al cliente


class DeviceBase(SQLModel):
    """Campos base de dispositivo"""
    brand: str = Field(max_length=50)
    model: str = Field(max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    imei: Optional[str] = Field(default=None, max_length=20)
    device_type: DeviceType = Field(default=DeviceType.SMARTPHONE)
    color: Optional[str] = Field(default=None, max_length=30)
    storage: Optional[str] = Field(default=None, max_length=20)  # ej: "128GB"
    password_pattern: Optional[str] = Field(default=None)  # Patrón/contraseña del dispositivo
    accessories: Optional[str] = Field(default=None)  # Accesorios que deja el cliente
    photos: Optional[str] = Field(default=None)  # URLs de fotos separadas por coma


class DeviceCreate(DeviceBase):
    """Schema para crear dispositivo"""
    customer_id: int


class DeviceUpdate(SQLModel):
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
    photos: Optional[str] = None


class Device(DeviceBase, table=True):
    """Modelo de dispositivo en la base de datos"""
    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customers.id", index=True)
    status: DeviceStatus = Field(default=DeviceStatus.REGISTERED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    customer: Optional["Customer"] = Relationship(back_populates="devices")  # type: ignore
    repairs: list["Repair"] = Relationship(back_populates="device", sa_relationship_kwargs={"lazy": "selectin"})  # type: ignore
