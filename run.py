import uvicorn
import os
import sys
from app.config import settings

def main():
    """
    Punto de entrada principal para ejecutar la aplicación en desarrollo.
    Lee automáticamente el puerto y el modo debug desde el archivo .env
    """
    print(f"🚀 Iniciando {settings.APP_NAME}...")
    print(f"📡 Puerto configurado: {settings.PORT}")
    print(f"🛠️  Modo Debug: {settings.DEBUG}")
    
    # Configurar nivel de logs: 'debug' solo si DEBUG es True, de lo contrario 'info' o 'warning'
    log_level = "debug" if settings.DEBUG else "info"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=log_level,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )

if __name__ == "__main__":
    main()
