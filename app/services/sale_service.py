from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from app.models.sale import Sale, SaleItem
from app.models.inventory import InventoryItem, MovementType
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.services.inventory_service import InventoryService
from fastapi import HTTPException, status

class SaleService:
    """Servicio de gestión de ventas"""

    def __init__(self, session: Session):
        self.session = session
        self.inventory_service = InventoryService(session)

    def create_sale(
        self,
        user_id: int,
        items_data: List[dict],
        payment_method: PaymentMethod,
        amount_paid: float,
        customer_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Sale:
        """Crear nueva venta (reducir stock y registrar pago)"""
        
        # Validar items
        total = 0.0
        sale_items = []

        for item_data in items_data:
            inventory_item_id = item_data["inventory_item_id"]
            quantity = item_data["quantity"]
            
            # Verificar stock
            inventory_item = self.inventory_service.get_item_by_id(inventory_item_id)
            if not inventory_item:
                raise ValueError(f"El producto con ID {inventory_item_id} no existe")
                
            if inventory_item.stock_quantity < quantity:
                raise ValueError(f"Stock insuficiente para {inventory_item.name}. Disponible: {inventory_item.stock_quantity}")
            
            unit_price = item_data.get("unit_price", inventory_item.unit_price)
            subtotal = unit_price * quantity
            total += subtotal
            
            sale_items.append({
                "inventory_item_id": inventory_item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
                "notes": item_data.get("notes")
            })

        if amount_paid < total:
            raise ValueError(f"El monto pagado (${amount_paid}) es menor al total (${total})")

        # Generar venta
        sale_number = self._generate_sale_number()
        
        sale = Sale(
            sale_number=sale_number,
            customer_id=customer_id,
            user_id=user_id,
            total=total,
            notes=notes
        )
        self.session.add(sale)
        self.session.flush() # Para obtener sale.id

        # Crear items y reducir stock
        for item_data in sale_items:
            # Reducir stock usando inventory_service
            self.inventory_service.adjust_stock(
                item_id=item_data["inventory_item_id"],
                quantity=-item_data["quantity"],
                reason=f"Venta {sale_number}",
                movement_type=MovementType.WITHDRAWAL,
                user_id=user_id
            )
            
            # Crear SaleItem
            sale_item = SaleItem(
                sale_id=sale.id,
                inventory_item_id=item_data["inventory_item_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"],
                notes=item_data["notes"]
            )
            self.session.add(sale_item)

        # Crear pago
        payment = Payment(
            sale_id=sale.id,
            amount=amount_paid, # Se podría registrar solo el total o lo pagado
            payment_method=payment_method,
            status=PaymentStatus.COMPLETED,
            notes=f"Pago por venta {sale_number}",
            processed_at=datetime.utcnow()
        )
        self.session.add(payment)

        self.session.commit()
        self.session.refresh(sale)
        return sale

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """Obtener venta por ID"""
        return self.session.get(Sale, sale_id)

    def get_sales(self, skip: int = 0, limit: int = 100) -> List[Sale]:
        """Obtener lista de ventas"""
        return self.session.exec(
            select(Sale).order_by(Sale.created_at.desc()).offset(skip).limit(limit)
        ).all()

    def _generate_sale_number(self) -> str:
        """Generar número único de venta"""
        today = datetime.now().strftime("%Y%m%d")
        last_sale = self.session.exec(
            select(Sale)
            .where(Sale.sale_number.like(f"VEN-{today}-%"))
            .order_by(Sale.sale_number.desc())
            .limit(1)
        ).first()

        if last_sale:
            last_num = int(last_sale.sale_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"VEN-{today}-{new_num:04d}"
