from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.repair import Repair


class PaymentMethod(str, Enum):
    """Métodos de pago"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    TRANSFER = "transfer"
    PAYPAL = "paypal"
    OTHER = "other"


class PaymentStatus(str, Enum):
    """Estado del pago"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentBase(SQLModel):
    """Campos base de pago"""
    amount: float = Field(ge=0)
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH)
    reference: Optional[str] = Field(default=None, max_length=100)  # Referencia/transacción
    notes: Optional[str] = Field(default=None)


class PaymentCreate(PaymentBase):
    """Schema para crear pago"""
    repair_id: int


class PaymentUpdate(SQLModel):
    """Schema para actualizar pago"""
    amount: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[PaymentStatus] = None


class Payment(PaymentBase, table=True):
    """Modelo de pago en la base de datos"""
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    repair_id: int = Field(foreign_key="repairs.id", index=True)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    # Relaciones
    repair: Optional["Repair"] = Relationship(back_populates="payments")  # type: ignore
