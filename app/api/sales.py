from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from app.database import get_session
from app.models.user import User
from app.schemas.sale import SaleCreateSchema, SaleResponse
from app.core.dependencies import get_current_user, require_role
from app.services.sale_service import SaleService

router = APIRouter()

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_data: SaleCreateSchema,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Crear nueva venta"""
    sale_service = SaleService(session)
    try:
        # Convert items to dict
        items_data = [item.model_dump() for item in sale_data.items]
        
        sale = sale_service.create_sale(
            user_id=current_user.id,
            items_data=items_data,
            payment_method=sale_data.payment_method,
            amount_paid=sale_data.amount_paid,
            customer_id=sale_data.customer_id,
            notes=sale_data.notes
        )
        return sale
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{sale_id}", response_model=SaleResponse)
def read_sale(
    sale_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener venta por ID"""
    sale_service = SaleService(session)
    sale = sale_service.get_sale_by_id(sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    return sale

@router.get("/", response_model=List[SaleResponse])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener todas las ventas"""
    sale_service = SaleService(session)
    sales = sale_service.get_sales(skip=skip, limit=limit)
    return sales
