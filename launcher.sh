#!/bin/bash

# ============================================
# Launcher para Careld POS
# ============================================

PROJECT_DIR="/home/kaber420/Documentos/python/proyectos-qwen/careld-pos-002"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VITE_CONFIG="$FRONTEND_DIR/vite.config.js"

echo "========================================"
echo "   🚀 Careld POS - Launcher"
echo "========================================"
echo ""

# Puerto por defecto
DEFAULT_PORT=8100
read -p "Puerto del backend [$DEFAULT_PORT]: " BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-$DEFAULT_PORT}

# Actualizar vite.config.js con el puerto seleccionado
sed -i "s/target: 'http:\/\/localhost:[0-9]*'/target: 'http:\/\/localhost:$BACKEND_PORT'/" "$VITE_CONFIG"
echo "✅ Proxy configurado para puerto $BACKEND_PORT"

echo ""
echo "Selecciona el modo de ejecución:"
echo ""
echo "1) Desarrollo (npm run dev + uvicorn)"
echo "2) Producción (solo frontend compilado)"
echo "3) Solo Backend (uvicorn)"
echo "4) Compilar Frontend (npm run build)"
echo ""
echo "q) Salir"
echo ""

read -p "Opción: " opcion

case $opcion in
    1)
        echo ""
        echo "▶ Iniciando modo DESARROLLO en puerto $BACKEND_PORT..."
        echo ""

        # Verificar si el venv existe
        if [ ! -d "$PROJECT_DIR/venv" ]; then
            echo "❌ Error: No se encontró el entorno virtual en $PROJECT_DIR/venv"
            echo "   ¿Necesitas crear uno? (s/n)"
            read crear_venv
            if [ "$crear_venv" = "s" ]; then
                cd "$PROJECT_DIR"
                python3 -m venv venv
                source venv/bin/activate
                pip install -r requirements.txt "bcrypt<4.1.0"
                echo "✅ Entorno virtual creado"
            else
                exit 1
            fi
        fi

        # Verificar si el backend ya está corriendo
        if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  El backend ya está corriendo en el puerto $BACKEND_PORT"
        else
            echo "▶ Iniciando Backend (uvicorn)..."
            cd "$PROJECT_DIR"
            source venv/bin/activate
            uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT &
            sleep 3
        fi

        # Verificar si el frontend ya está corriendo en el puerto 5173
        if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  El frontend ya está corriendo en el puerto 5173"
        else
            echo "▶ Iniciando Frontend (Vite)..."
            cd "$FRONTEND_DIR"
            npm run dev &
            sleep 3
        fi

        echo ""
        echo "========================================"
        echo "✅ Servicios iniciados:"
        echo "   Frontend: http://localhost:5173"
        echo "   Backend:  http://localhost:$BACKEND_PORT"
        echo "   Docs:     http://localhost:$BACKEND_PORT/docs"
        echo "========================================"
        echo ""
        echo "Presiona Ctrl+C para detener los servicios"
        echo ""

        wait
        ;;

    2)
        echo ""
        echo "▶ Iniciando modo PRODUCCIÓN en puerto $BACKEND_PORT..."
        echo ""

        # Verificar si existe la build
        if [ ! -d "$FRONTEND_DIR/dist" ]; then
            echo "❌ No se encontró la build del frontend"
            echo "   ¿Compilamos primero? (s/n)"
            read compilar
            if [ "$compilar" = "s" ]; then
                cd "$FRONTEND_DIR"
                npm run build
            else
                exit 1
            fi
        fi

        # Verificar si el backend ya está corriendo
        if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  El backend ya está corriendo en el puerto $BACKEND_PORT"
        else
            echo "▶ Iniciando Backend..."
            cd "$PROJECT_DIR"
            source venv/bin/activate
            uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
            sleep 3
        fi

        echo ""
        echo "========================================"
        echo "✅ Servicios iniciados:"
        echo "   App:   http://localhost:$BACKEND_PORT"
        echo "   Docs:  http://localhost:$BACKEND_PORT/docs"
        echo "========================================"
        echo ""

        wait
        ;;

    3)
        echo ""
        echo "▶ Iniciando solo Backend en puerto $BACKEND_PORT..."
        echo ""

        cd "$PROJECT_DIR"
        source venv/bin/activate
        uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT
        ;;

    4)
        echo ""
        echo "▶ Compilando Frontend..."
        echo ""
        cd "$FRONTEND_DIR"
        npm run build

        if [ -d "$FRONTEND_DIR/dist" ]; then
            echo ""
            echo "✅ Frontend compilado exitosamente"
            echo "   Build en: $FRONTEND_DIR/dist"
        else
            echo ""
            echo "❌ Error al compilar"
        fi
        ;;

    q|Q)
        echo "👋 Hasta luego!"
        exit 0
        ;;

    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac
