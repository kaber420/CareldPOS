from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.repair import Repair


class PaymentService:
    """Servicio de gestión de pagos"""

    def __init__(self, session: Session):
        self.session = session

    def create_payment(
        self,
        repair_id: int,
        amount: float,
        payment_method: PaymentMethod = PaymentMethod.CASH,
        reference: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Payment:
        """Crear nuevo pago"""
        # Verificar reparación
        repair = self.session.get(Repair, repair_id)
        if not repair:
            raise ValueError("Repair not found")

        payment = Payment(
            repair_id=repair_id,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            status=PaymentStatus.PENDING
        )

        # Auto-completar si es efectivo
        if payment_method == PaymentMethod.CASH:
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Obtener pago por ID"""
        return self.session.get(Payment, payment_id)

    def get_payments_by_repair(self, repair_id: int) -> List[Payment]:
        """Obtener pagos de una reparación"""
        return self.session.exec(
            select(Payment).where(Payment.repair_id == repair_id)
        ).all()

    def get_payments_by_status(
        self,
        status: PaymentStatus
    ) -> List[Payment]:
        """Obtener pagos por estado"""
        return self.session.exec(
            select(Payment).where(Payment.status == status)
        ).all()

    def complete_payment(self, payment_id: int) -> Optional[Payment]:
        """Marcar pago como completado"""
        payment = self.session.get(Payment, payment_id)
        if not payment:
            return None

        payment.status = PaymentStatus.COMPLETED
        payment.processed_at = datetime.utcnow()
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        # Verificar si todos los pagos de la reparación están completados
        self._check_repair_payments(payment.repair_id)

        return payment

    def cancel_payment(self, payment_id: int) -> Optional[Payment]:
        """Cancelar pago"""
        payment = self.session.get(Payment, payment_id)
        if not payment:
            return None

        if payment.status == PaymentStatus.COMPLETED:
            raise ValueError("Cannot cancel completed payment")

        payment.status = PaymentStatus.CANCELLED
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def refund_payment(self, payment_id: int) -> Optional[Payment]:
        """Reembolsar pago"""
        payment = self.session.get(Payment, payment_id)
        if not payment:
            return None

        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Can only refund completed payments")

        payment.status = PaymentStatus.REFUNDED
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def get_payment_summary(self, repair_id: int) -> dict:
        """Obtener resumen de pagos de una reparación"""
        repair = self.session.get(Repair, repair_id)
        if not repair:
            raise ValueError("Repair not found")

        payments = self.get_payments_by_repair(repair_id)

        total_paid = sum(
            p.amount for p in payments
            if p.status == PaymentStatus.COMPLETED
        )
        total_pending = sum(
            p.amount for p in payments
            if p.status == PaymentStatus.PENDING
        )
        balance = (repair.final_cost or 0) - total_paid

        return {
            "repair_id": repair_id,
            "repair_number": repair.repair_number,
            "final_cost": repair.final_cost,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "balance": balance,
            "payments_count": len(payments),
            "is_fully_paid": balance <= 0,
        }

    def _check_repair_payments(self, repair_id: int) -> None:
        """Verificar si todos los pagos están completados y actualizar reparación"""
        payments = self.get_payments_by_repair(repair_id)

        if all(p.status == PaymentStatus.COMPLETED for p in payments):
            repair = self.session.get(Repair, repair_id)
            if repair and repair.status != "delivered":
                repair.status = RepairStatus.DELIVERED
                repair.delivered_at = datetime.utcnow()
                self.session.add(repair)
                self.session.commit()

    def get_daily_total(
        self,
        date: Optional[datetime] = None
    ) -> float:
        """Obtener total cobrado en el día"""
        if date is None:
            date = datetime.utcnow()

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        payments = self.session.exec(
            select(Payment).where(
                (Payment.status == PaymentStatus.COMPLETED) &
                (Payment.created_at >= start_date) &
                (Payment.created_at <= end_date)
            )
        ).all()

        return sum(p.amount for p in payments)

    def get_pending_payments(self) -> List[Payment]:
        """Obtener pagos pendientes"""
        return self.session.exec(
            select(Payment).where(Payment.status == PaymentStatus.PENDING)
        ).all()
