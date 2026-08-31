#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# SCRIPT DE INSTALACIÓN - ERGONOMETAPP V2.0
# ═══════════════════════════════════════════════════════════════════════════════

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║        🚀 INSTALACIÓN ERGONOMETAPP V2.0                                  ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Paso 1: Verificar Python
echo -e "${BLUE}[1/5] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3 no encontrado. Por favor instálalo primero.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION encontrado${NC}"
echo ""

# Paso 2: Crear entorno virtual
echo -e "${BLUE}[2/5] Creando entorno virtual...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ venv ya existe, saltando creación${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
fi
echo ""

# Paso 3: Activar entorno virtual
echo -e "${BLUE}[3/5] Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# Paso 4: Instalar dependencias
echo -e "${BLUE}[4/5] Instalando dependencias...${NC}"
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# Paso 5: Inicializar BD
echo -e "${BLUE}[5/5] Inicializando base de datos...${NC}"
python3 << 'PYTHON'
import os
from app import app, db

with app.app_context():
    # Crear directorios necesarios
    os.makedirs('database', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('reportes', exist_ok=True)
    
    # Crear tablas
    db.create_all()
    
    print("✓ Base de datos creada")
PYTHON
echo -e "${GREEN}✓ BD inicializada${NC}"
echo ""

# Resumen final
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ INSTALACIÓN COMPLETADA                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 PRÓXIMOS PASOS:${NC}"
echo ""
echo "1️⃣  Activar entorno virtual (si no está activado):"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "2️⃣  Ejecutar la aplicación:"
echo -e "   ${BLUE}python app.py${NC}"
echo ""
echo "3️⃣  Abrir en navegador:"
echo -e "   ${BLUE}http://localhost:5000${NC}"
echo ""
echo "📊 Dashboard disponible en:"
echo -e "   ${BLUE}http://localhost:5000/dashboard${NC}"
echo ""

