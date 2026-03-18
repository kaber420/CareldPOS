from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentBase(BaseModel):
    """Schema base de pago"""
    amount: float = Field(ge=0)
    payment_method: PaymentMethod = PaymentMethod.CASH
    reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema para crear pago"""
    repair_id: int


class PaymentUpdate(BaseModel):
    """Schema para actualizar pago"""
    amount: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[PaymentStatus] = None


class PaymentResponse(PaymentBase):
    """Schema de respuesta de pago"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_id: int
    status: PaymentStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
