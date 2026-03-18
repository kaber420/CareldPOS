from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models.user import User
from app.models.device import Device, DeviceStatus
from app.models.customer import Customer
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Registrar un nuevo dispositivo"""
    # Verificar que el cliente existe
    customer = session.get(Customer, device_data.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Verificar IMEI si está presente
    if device_data.imei:
        existing = session.exec(
            select(Device).where(Device.imei == device_data.imei)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IMEI already registered"
            )

    device = Device.model_validate(device_data)
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.get("/", response_model=List[DeviceResponse])
def read_devices(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    status_filter: Optional[DeviceStatus] = Query(None, alias="status", description="Filtrar por estado"),
    search: Optional[str] = Query(None, description="Buscar por marca, modelo o cliente"),
    device_type: Optional[str] = Query(None, description="Filtrar por tipo de dispositivo"),
    brand: Optional[str] = Query(None, description="Filtrar por marca"),
    ready_for_delivery: Optional[bool] = Query(None, description="Solo dispositivos listos para entrega"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Listar dispositivos con filtros opcionales"""
    query = select(Device).join(Customer, isouter=True)

    if customer_id:
        query = query.where(Device.customer_id == customer_id)

    if status_filter:
        query = query.where(Device.status == status_filter)
    # Ignorar ready_for_delivery - mostrar todos los dispositivos
    # elif ready_for_delivery is True:
    #     query = query.where(Device.status.in_([DeviceStatus.READY, DeviceStatus.DELIVERED]))

    if search:
        query = query.where(
            (Device.brand.ilike(f"%{search}%")) |
            (Device.model.ilike(f"%{search}%")) |
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%"))
        )

    if device_type:
        query = query.where(Device.device_type == device_type)

    if brand:
        query = query.where(Device.brand.ilike(f"%{brand}%"))

    # Cargar relación customer
    query = query.options(selectinload(Device.customer))

    devices = session.exec(query.offset(skip).limit(limit)).all()
    
    # Convertir nombres de archivo de fotos en URLs completas
    for device in devices:
        if device.photos:
            photo_names = [p.strip() for p in device.photos.split(',')]
            device.photos = ','.join([
                f'/api/v1/uploads/photo/{name}' if not name.startswith('/api/') else name
                for name in photo_names if name
            ])
    
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
def read_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener dispositivo por ID"""
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualizar dispositivo"""
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    update_data = device_data.model_dump(exclude_unset=True)

    if "imei" in update_data and update_data["imei"]:
        existing = session.exec(
            select(Device).where(
                (Device.imei == update_data["imei"]) &
                (Device.id != device_id)
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IMEI already registered"
            )

    for field, value in update_data.items():
        setattr(device, field, value)

    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Eliminar dispositivo"""
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    session.delete(device)
    session.commit()
    return {"message": "Device deleted successfully"}


@router.get("/customer/{customer_id}", response_model=List[DeviceResponse])
def read_customer_devices(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener todos los dispositivos de un cliente"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    devices = session.exec(
        select(Device).where(Device.customer_id == customer_id)
    ).all()
    return devices
