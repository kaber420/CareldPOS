from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Crear un nuevo cliente"""
    # Verificar si el cliente ya existe (por email o teléfono)
    if customer_data.email:
        existing = session.exec(
            select(Customer).where(Customer.email == customer_data.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    existing_phone = session.exec(
        select(Customer).where(Customer.phone == customer_data.phone)
    ).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    customer = Customer.model_validate(customer_data)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("/", response_model=List[CustomerResponse])
def read_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Buscar por nombre, email o teléfono"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Listar clientes con búsqueda opcional"""
    query = select(Customer).where(Customer.is_active == True)

    if search:
        query = query.where(
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%"))
        )

    customers = session.exec(query.offset(skip).limit(limit)).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener cliente por ID"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualizar cliente"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    update_data = customer_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"]:
        existing = session.exec(
            select(Customer).where(
                (Customer.email == update_data["email"]) &
                (Customer.id != customer_id)
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    if "phone" in update_data:
        existing = session.exec(
            select(Customer).where(
                (Customer.phone == update_data["phone"]) &
                (Customer.id != customer_id)
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

    for field, value in update_data.items():
        setattr(customer, field, value)

    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Eliminar cliente (soft delete)"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    customer.is_active = False
    session.add(customer)
    session.commit()
    return {"message": "Customer deactivated successfully"}
