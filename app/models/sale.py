from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.inventory import InventoryItem
    from app.models.payment import Payment

class SaleBase(SQLModel):
    """Base fields for a Sale"""
    total: float = Field(ge=0)
    notes: Optional[str] = Field(default=None)

class SaleCreate(SaleBase):
    """Schema to create a sale"""
    customer_id: Optional[int] = None
    user_id: int

class Sale(SaleBase, table=True):
    """Sale model in database"""
    __tablename__ = "sales"

    id: Optional[int] = Field(default=None, primary_key=True)
    sale_number: str = Field(unique=True, index=True)
    customer_id: Optional[int] = Field(default=None, foreign_key="customers.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship() # No back_populates needed for now
    user: Optional["User"] = Relationship()
    items: List["SaleItem"] = Relationship(back_populates="sale", sa_relationship_kwargs={"lazy": "selectin"})
    payments: List["Payment"] = Relationship(back_populates="sale", sa_relationship_kwargs={"lazy": "selectin"})

class SaleItemBase(SQLModel):
    """Base fields for Sale Item"""
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(default=0.0, ge=0)
    subtotal: float = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(default=None)

class SaleItem(SaleItemBase, table=True):
    """Sale Item model in database"""
    __tablename__ = "sale_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id", index=True)
    inventory_item_id: Optional[int] = Field(default=None, foreign_key="inventory_items.id")
    repair_id: Optional[int] = Field(default=None, foreign_key="repairs.id")
    service_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sale: Optional["Sale"] = Relationship(back_populates="items")
    inventory_item: Optional["InventoryItem"] = Relationship()
