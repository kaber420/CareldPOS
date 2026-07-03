import uvicorn
import os
import sys
import argparse

def main():
    """
    Punto de entrada principal para ejecutar la aplicación.
    Soporta configuraciones mediante flags y carga de variables de entorno.
    """
    parser = argparse.ArgumentParser(description="Launcher de CareldPOS")
    parser.add_argument(
        "--setup", "-s", 
        action="store_true", 
        help="Iniciar el proceso de configuración interactiva"
    )
    
    args = parser.parse_args()

    if args.setup:
        from app.setup_cli import run_setup
        run_setup()
        return

    if not os.path.exists(".env"):
        print("\n" + "="*40)
        print("❌ Error: Falta archivo .env")
        print("="*40)
        print("\nPara configurar la aplicación ejecutá:")
        print("  python3 run.py --setup\n")
        sys.exit(1)

    from app.config import settings

    print("\n" + "="*40)
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 Puerto: {settings.PORT}")
    print(f"🛠️  Modo Debug: {settings.DEBUG}")
    print("="*40 + "\n")
    
    # Configurar nivel de logs: 'debug' solo si DEBUG es True, de lo contrario 'info'
    log_level = "debug" if settings.DEBUG else "info"
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=log_level,
            proxy_headers=True,
            forwarded_allow_ips="*"
        )
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()
