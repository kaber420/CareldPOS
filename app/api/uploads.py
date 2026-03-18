import os
import uuid
import magic
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from app.database import SessionLocal
from app.models.device import Device

router = APIRouter()

# Directorio seguro fuera del alcance estático público
UPLOAD_DIR = "data/uploads"

# Extensiones permitidas
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}

# MIME types permitidos - validación REAL del contenido del archivo
ALLOWED_MIME_TYPES = {
    # Imágenes
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    # Videos cortos (para documentación de reparaciones)
    "video/mp4": ".mp4",
    "video/quicktime": ".mov"
}

# Límites de tamaño
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB para imágenes
MAX_VIDEO_SIZE = 30 * 1024 * 1024  # 30MB para videos
MAX_VIDEO_DURATION = 30  # 30 segundos máximo


def validate_file(filename: str, size: int) -> tuple[bool, str]:
    """
    Validar extensión y tamaño del archivo.
    Returns: (es_valido, mensaje_error)
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Extensión no permitida: {ext}. Solo {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Determinar límite según tipo
    is_video = ext in {".mp4", ".mov"}
    max_size = MAX_VIDEO_SIZE if is_video else MAX_IMAGE_SIZE
    
    if size > max_size:
        tipo = "video" if is_video else "imagen"
        return False, f"Archivo muy grande. Máximo {max_size // 1024 // 1024}MB para {tipo}s"
    
    return True, ""


@router.post("/{device_id}")
async def upload_photo(device_id: int, file: UploadFile = File(...)):
    """
    Subir foto o video corto de dispositivo.
    
    Valida:
    - Extensión del archivo
    - Tamaño máximo
    - MIME type REAL del contenido (no solo la extensión)
    - Path traversal attacks
    """
    # Validar tamaño
    content = await file.read()
    file_size = len(content)
    
    es_valido, error_msg = validate_file(file.filename, file_size)
    if not es_valido:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Validar MIME type REAL usando python-magic
    # Esto previene ataques donde un archivo .jpg contiene código malicioso
    mime = magic.Magic(mime=True)
    actual_mime = mime.from_buffer(content[:1024])  # Leer primeros bytes
    
    if actual_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. MIME real: {actual_mime}. "
                   f"Tipos permitidos: {', '.join(ALLOWED_MIME_TYPES.keys())}"
        )
    
    # Verificar que la extensión coincida con el MIME type
    ext = os.path.splitext(file.filename)[1].lower()
    expected_ext = ALLOWED_MIME_TYPES[actual_mime]
    if ext != expected_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión '{ext}' no coincide con el tipo de archivo '{actual_mime}'. "
                   f"Se esperaba '{expected_ext}'"
        )
    
    # Crear nombre único con UUID (elimina cualquier información del nombre original)
    filename = f"{uuid.uuid4()}{expected_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Guardar archivo
    with open(filepath, "wb") as f:
        f.write(content)

    # Actualizar dispositivo con el nombre del archivo
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            # Eliminar archivo si el dispositivo no existe
            os.remove(filepath)
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

        # Guardar solo el nombre del archivo
        if device.photos:
            device.photos = f"{device.photos},{filename}"
        else:
            device.photos = filename

        db.commit()
        db.refresh(device)

        return {
            "url": f"/api/v1/uploads/photo/{filename}",
            "device_id": device_id,
            "filename": filename,
            "mime_type": actual_mime,
            "size": file_size
        }
    finally:
        db.close()


@router.get("/photo/{filename}")
async def get_photo(filename: str):
    """
    Obtener foto o video de dispositivo de forma segura.
    
    Valida:
    - Path traversal attacks
    - Extensión permitida
    - Que el archivo exista
    """
    # Validar que el nombre del archivo sea seguro
    if not filename or ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # Determinar MIME type para el response
    is_video = ext in {".mp4", ".mov"}
    media_type = "video/mp4" if is_video else f"image/{ext[1:]}"

    # Servir archivo de forma segura
    return FileResponse(
        filepath,
        media_type=media_type,
        filename=filename,
        headers={
            "Cache-Control": "public, max-age=31536000" if not is_video else "public, max-age=3600"
        }
    )


@router.get("/photo/{filename}/stream")
async def stream_photo(filename: str):
    """
    Stream de foto/video para dispositivos móviles.
    Útil para videos o imágenes grandes.
    """
    if not filename or ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    is_video = ext in {".mp4", ".mov"}
    
    def iterfile():
        with open(filepath, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(
        iterfile(),
        media_type="video/mp4" if is_video else "image/jpeg",
        headers={
            "Content-Disposition": f"inline; filename={filename}",
            "Accept-Ranges": "bytes"
        }
    )
