from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.repair import Repair
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Registrar nuevo pago"""
    # Verificar que la reparación existe
    repair = session.get(Repair, payment_data.repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )

    # Verificar que la reparación esté completada
    if repair.status.value not in ["completed", "delivered"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment can only be made for completed repairs"
        )

    payment = Payment.model_validate(payment_data)

    # Marcar como completado si es efectivo
    if payment.payment_method == PaymentMethod.CASH:
        payment.status = PaymentStatus.COMPLETED
        payment.processed_at = datetime.utcnow()

    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@router.get("/", response_model=List[PaymentResponse])
def read_payments(
    skip: int = 0,
    limit: int = 100,
    repair_id: Optional[int] = Query(None),
    status_filter: Optional[PaymentStatus] = Query(None, alias="status"),
    payment_method: Optional[PaymentMethod] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Listar pagos con filtros"""
    query = select(Payment)

    if repair_id:
        query = query.where(Payment.repair_id == repair_id)
    if status_filter:
        query = query.where(Payment.status == status_filter)
    if payment_method:
        query = query.where(Payment.payment_method == payment_method)

    query = query.order_by(Payment.created_at.desc())
    payments = session.exec(query.offset(skip).limit(limit)).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def read_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener pago por ID"""
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualizar pago"""
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    update_data = payment_data.model_dump(exclude_unset=True)

    # Si se cambia el estado a completado, establecer processed_at
    if "status" in update_data:
        if update_data["status"] == PaymentStatus.COMPLETED and not payment.processed_at:
            payment.processed_at = datetime.utcnow()
        elif update_data["status"] == PaymentStatus.CANCELLED:
            payment.processed_at = None

    for field, value in update_data.items():
        if value is not None:
            setattr(payment, field, value)

    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@router.post("/{payment_id}/complete", response_model=PaymentResponse)
def complete_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Marcar pago como completado"""
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    payment.status = PaymentStatus.COMPLETED
    payment.processed_at = datetime.utcnow()

    # Actualizar estado de la reparación a delivered si todos los pagos están completados
    repair = session.get(Repair, payment.repair_id)
    if repair:
        all_payments = session.exec(
            select(Payment).where(Payment.repair_id == repair.id)
        ).all()
        if all(p.status == PaymentStatus.COMPLETED for p in all_payments):
            repair.status = "delivered"
            repair.delivered_at = datetime.utcnow()
            session.add(repair)

    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    current_user: User = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """Eliminar pago (solo admin)"""
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete completed payment. Use refund instead."
        )

    session.delete(payment)
    session.commit()
    return {"message": "Payment deleted successfully"}


@router.get("/repair/{repair_id}/summary")
def get_payment_summary(
    repair_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener resumen de pagos de una reparación"""
    repair = session.get(Repair, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found"
        )

    payments = session.exec(
        select(Payment).where(Payment.repair_id == repair_id)
    ).all()

    total_paid = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)
    total_pending = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)
    balance = (repair.final_cost or 0) - total_paid

    return {
        "repair_id": repair_id,
        "repair_number": repair.repair_number,
        "final_cost": repair.final_cost,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "balance": balance,
        "payments_count": len(payments),
        "payments": payments,
    }
