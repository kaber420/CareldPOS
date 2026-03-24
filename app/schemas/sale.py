from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.sale import SaleBase, SaleItemBase
from app.schemas.customer import CustomerResponse
from app.schemas.payment import PaymentResponse

# Items
class SaleItemCreate(SaleItemBase):
    inventory_item_id: Optional[int] = None
    repair_id: Optional[int] = None
    service_name: Optional[str] = None

class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    inventory_item_id: Optional[int] = None
    repair_id: Optional[int] = None
    service_name: Optional[str] = None
    created_at: datetime
    
    # Podría incluir detalles del item
    class Config:
        from_attributes = True

# Sale
class SaleCreateSchema(SaleBase):
    customer_id: Optional[int] = None
    items: List[SaleItemCreate]
    payment_method: str
    amount_paid: float

class SaleResponse(SaleBase):
    id: int
    sale_number: str
    user_id: int
    customer_id: Optional[int] = None
    created_at: datetime
    
    items: List[SaleItemResponse] = []
    payments: List[PaymentResponse] = []
    customer: Optional[CustomerResponse] = None

    class Config:
        from_attributes = True
