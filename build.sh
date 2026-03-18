#!/bin/bash

# Script de build y deploy para SBC ARM64

echo "🔨 Construyendo frontend..."
cd frontend

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Build del frontend
echo "📦 Construyendo..."
npm run build

echo "✅ Build completado!"
echo ""
echo "📁 Archivos generados en: frontend/dist/"
echo ""
echo "Para deployar a tu SBC:"
echo "  scp -r dist/* user@tu-sbc:/opt/pos-frontend/"
echo ""
echo "O copia los archivos a app/static/ para servir desde FastAPI:"
echo "  cp -r dist/* ../app/static/"
