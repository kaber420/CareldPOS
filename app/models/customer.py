from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.device import Device


class CustomerBase(SQLModel):
    """Campos base de cliente"""
    name: str = Field(max_length=100, index=True)
    email: Optional[str] = Field(default=None, max_length=100)
    phone: str = Field(max_length=20, index=True)
    alternate_phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None)


class CustomerCreate(CustomerBase):
    """Schema para crear cliente"""
    pass


class CustomerUpdate(SQLModel):
    """Schema para actualizar cliente"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class Customer(CustomerBase, table=True):
    """Modelo de cliente en la base de datos"""
    __tablename__ = "customers"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relación con dispositivos
    devices: list["Device"] = Relationship(back_populates="customer", sa_relationship_kwargs={"lazy": "selectin"})  # type: ignore
