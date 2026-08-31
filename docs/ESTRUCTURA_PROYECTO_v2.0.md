# 📁 ESTRUCTURA PROYECTO ERGONOMETAPP V2.0

## Tabla de contenidos con ubicaciones de archivos

```
ergonometapp-v2.0/
│
├── 📄 app.py ........................... ARCHIVO PRINCIPAL (Flask app)
├── 📄 config.py ........................ CONFIGURACIÓN DEL PROYECTO
├── 📄 requirements.txt ................. DEPENDENCIAS PYTHON
├── 📄 setup.sh ......................... SCRIPT DE INSTALACIÓN
├── 📄 database_init.py ................. INICIALIZACIÓN BD
├── 📄 README.md ........................ DOCUMENTACIÓN PRINCIPAL
│
├── 📁 models/
│   ├── __init__.py
│   ├── database.py ..................... DEFINICIÓN DE TABLAS
│   ├── calculadores.py ................. CÁLCULOS REBA
│   ├── ley_silla.py .................... CÁLCULOS LEY SILLA
│   ├── lest.py ......................... CÁLCULOS LEST
│   ├── apendice_i.py ................... CÁLCULOS APÉNDICE I
│   ├── apendice_ii.py .................. CÁLCULOS APÉNDICE II
│   └── kuorinka.py ..................... CÁLCULOS KUORINKA
│
├── 📁 routes/
│   ├── __init__.py
│   ├── main.py ......................... RUTAS PRINCIPALES
│   ├── dashboard.py .................... DASHBOARD
│   │
│   └── 📁 metodos/ (MÉTODOS ERGONÓMICOS)
│       ├── __init__.py
│       ├── reba.py ..................... REBA (5 pasos)
│       ├── ley_silla.py ................ LEY SILLA (3 pasos)
│       ├── lest.py ..................... LEST (4 pasos)
│       ├── apendice_i.py ............... APÉNDICE I (3 pasos)
│       ├── apendice_ii.py .............. APÉNDICE II (3 pasos)
│       └── kuorinka.py ................. KUORINKA (2 pasos)
│
├── 📁 templates/ (HTML JINJA2)
│   ├── base.html ....................... PLANTILLA BASE
│   ├── index.html ....................... PÁGINA PRINCIPAL
│   ├── error.html ....................... PÁGINA DE ERROR
│   ├── dashboard.html ................... DASHBOARD CON GRÁFICOS
│   ├── metodos.html ..................... LISTADO DE MÉTODOS
│   ├── trabajadores.html ................ GESTIÓN DE TRABAJADORES
│   ├── trabajador_nuevo.html ............ NUEVO TRABAJADOR
│   │
│   └── 📁 metodos/
│       ├── 📁 reba/
│       │   ├── paso1_datos.html
│       │   ├── paso2_grupoA.html
│       │   ├── paso3_grupoB.html
│       │   ├── paso4_carga_agarre.html
│       │   └── paso5_resultado.html
│       │
│       ├── 📁 ley_silla/
│       │   ├── paso1_datos.html
│       │   ├── paso2_factores.html
│       │   └── paso3_resultado.html
│       │
│       ├── 📁 lest/
│       │   ├── paso1_datos.html
│       │   ├── paso2_carga_entorno.html
│       │   ├── paso3_mental_psico.html
│       │   └── paso4_tiempo_resultado.html
│       │
│       ├── 📁 apendice_i/
│       │   ├── paso1_datos.html
│       │   ├── paso2_parametros.html
│       │   └── paso3_resultado.html
│       │
│       ├── 📁 apendice_ii/
│       │   ├── paso1_datos.html
│       │   ├── paso2_parametros.html
│       │   └── paso3_resultado.html
│       │
│       └── 📁 kuorinka/
│           ├── paso1_datos.html
│           ├── paso2_preguntas.html
│           └── paso3_resultado.html
│
├── 📁 static/
│   ├── 📁 css/
│   │   └── style.css ................... ESTILOS GLOBALES
│   │
│   ├── 📁 js/
│   │   ├── charts.js ................... GRÁFICOS (CHART.JS)
│   │   ├── dashboard.js ................ LÓGICA DASHBOARD
│   │   ├── kinovea.js .................. HERRAMIENTA KINOVEA (REBA)
│   │   └── forms.js .................... VALIDACIÓN DE FORMULARIOS
│   │
│   └── 📁 images/
│       └── logo.png
│
├── 📁 database/
│   └── ergonometapp.db ................. BASE DE DATOS SQLITE (CREADA AL INSTALAR)
│
├── 📁 reportes/
│   └── (Reportes generados aquí)
│
├── 📁 docs/ (DOCUMENTACIÓN ADICIONAL)
│   ├── ARQUITECTURA.md ................. ARQUITECTURA DEL PROYECTO
│   ├── API.md .......................... DOCUMENTACIÓN DE ENDPOINTS
│   ├── METODOS.md ...................... DETALLES DE CÁLCULOS
│   ├── DATABASE.md ..................... SCHEMA DE BD
│   └── DESARROLLO.md ................... GUÍA PARA DESARROLLADORES
│
└── 📁 tests/ (TESTING - OPCIONAL)
    ├── test_reba.py
    ├── test_ley_silla.py
    ├── test_lest.py
    ├── test_apendices.py
    └── test_kuorinka.py
```

---

## 📋 DÓNDE ESTÁ CADA ARCHIVO

### Archivos generados en las sesiones anteriores (descarga de outputs):

```
DESCRIPCIÓN                           ARCHIVO                          UBICACIÓN EN PROYECTO
════════════════════════════════════════════════════════════════════════════════

CÓDIGO PYTHON - MÉTODOS
─────────────────────────────────────────────────────────────────────────────
Cálculos REBA                        models_calculadores.py           → models/calculadores.py
Cálculos Ley SILLA                   models_ley_silla.py              → models/ley_silla.py
Cálculos LEST                        models_lest.py                   → models/lest.py
Cálculos Apéndice I                  models_apendice_i.py             → models/apendice_i.py
Cálculos Apéndice II                 models_apendice_ii.py            → models/apendice_ii.py
Cálculos Kuorinka                    models_kuorinka.py               → models/kuorinka.py

Rutas REBA                           routes_reba.py                   → routes/metodos/reba.py
Rutas Ley SILLA                      routes_ley_silla.py              → routes/metodos/ley_silla.py
Rutas LEST                           routes_lest.py                   → routes/metodos/lest.py
Rutas Apéndice I                     routes_apendice_i.py             → routes/metodos/apendice_i.py
Rutas Apéndice II                    routes_apendice_ii.py            → routes/metodos/apendice_ii.py
Rutas Kuorinka                       routes_kuorinka.py               → routes/metodos/kuorinka.py

TEMPLATES HTML - MÉTODOS
─────────────────────────────────────────────────────────────────────────────
Apéndice I Paso 2                    paso2_apendice_ii.html           → templates/metodos/apendice_ii/paso2_parametros.html
Apéndice I Paso 3                    paso3_apendice_ii.html           → templates/metodos/apendice_ii/paso3_resultado.html
Apéndice I Completo                  templates_apendice_i.html        → templates/metodos/apendice_i/paso2_parametros.html
                                                                         templates/metodos/apendice_i/paso3_resultado.html
Kuorinka Paso 2                      paso2_kuorinka.html              → templates/metodos/kuorinka/paso2_preguntas.html
Kuorinka Paso 3                      paso3_kuorinka.html              → templates/metodos/kuorinka/paso3_resultado.html

JavaScript - Herramientas
─────────────────────────────────────────────────────────────────────────────
Kinovea (REBA)                       kinovea.js                       → static/js/kinovea.js

NUEVOS ARCHIVOS GENERADOS ESTA SESIÓN
─────────────────────────────────────────────────────────────────────────────
Aplicación principal                 app.py                           → app.py (RAÍZ)
Configuración                        config.py                        → config.py (RAÍZ)
Dependencias                         requirements.txt                 → requirements.txt (RAÍZ)
Script instalación                   setup.sh                         → setup.sh (RAÍZ)
Inicialización BD                    database_init.py                 → database_init.py (RAÍZ)
Dashboard                            dashboard.html                   → templates/dashboard.html
Rutas principales                    routes_main.py                   → routes/main.py
Rutas dashboard                      routes_dashboard.py              → routes/dashboard.py
README                               PROYECTO_COMPLETO_v2.0_README.md → README.md

```

---

## 🚀 INSTALACIÓN DESDE 0

### Paso 1: Crear estructura de carpetas

```bash
mkdir -p ergonometapp-v2.0
cd ergonometapp-v2.0

# Crear estructura
mkdir -p models routes/metodos templates templates/metodos/{reba,ley_silla,lest,apendice_i,apendice_ii,kuorinka}
mkdir -p static/{css,js,images} database reportes docs tests
```

### Paso 2: Copiar archivos

```bash
# Descargar archivos de /mnt/user-data/outputs/ y copiarlos:

# Archivos raíz
cp app.py .
cp config.py .
cp requirements.txt .
cp setup.sh .
chmod +x setup.sh
cp database_init.py .
cp README.md .

# Modelos
cp models_*.py models/
mv models/models_calculadores.py models/calculadores.py
mv models/models_ley_silla.py models/ley_silla.py
# ... etc

# Rutas
cp routes_main.py routes/main.py
cp routes_dashboard.py routes/dashboard.py
cp routes_*.py routes/metodos/
# ... etc

# Templates
cp dashboard.html templates/
cp paso*.html templates/metodos/apendice_i/
cp paso*.html templates/metodos/apendice_ii/
cp paso*.html templates/metodos/kuorinka/
# ... etc

# JavaScript
cp kinovea.js static/js/
cp charts.js static/js/
```

### Paso 3: Instalar

```bash
# Ejecutar script de instalación
bash setup.sh

# O manual:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database_init.py
```

### Paso 4: Ejecutar

```bash
python app.py
```

**¡Listo!** Abre http://localhost:5000

---

## 📊 ENDPOINTS DISPONIBLES

```
MÉTODOS
─────────────────────────────────────────────────────────────────────────
REBA                    GET  /reba/nueva
                        POST /reba/<uuid>/paso2
                        POST /reba/<uuid>/paso3
                        POST /reba/<uuid>/paso4
                        POST /reba/<uuid>/paso5
                        
Ley SILLA               GET  /ley-silla/nueva
                        POST /ley-silla/<uuid>/paso2
                        POST /ley-silla/<uuid>/paso3
                        
LEST                    GET  /lest/nueva
                        POST /lest/<uuid>/paso2
                        POST /lest/<uuid>/paso3
                        POST /lest/<uuid>/paso4
                        
Apéndice I              GET  /apendice-i/nueva
                        POST /apendice-i/<uuid>/paso2
                        POST /apendice-i/<uuid>/paso3
                        
Apéndice II             GET  /apendice-ii/nueva
                        POST /apendice-ii/<uuid>/paso2
                        POST /apendice-ii/<uuid>/paso3
                        
Kuorinka                GET  /cuestionario-nordico/nueva
                        POST /cuestionario-nordico/<uuid>/paso2
                        GET  /cuestionario-nordico/<uuid>/resultado

PRINCIPALES
─────────────────────────────────────────────────────────────────────────
Inicio                  GET  /
Métodos                 GET  /metodos
Trabajadores            GET  /trabajadores
Nuevo trabajador        GET  /trabajadores/nuevo
Dashboard               GET  /dashboard
Ayuda                   GET  /help
```

---

## 🔧 ARCHIVOS __init__.py NECESARIOS

Crear archivos vacíos en:

```
models/__init__.py
routes/__init__.py
routes/metodos/__init__.py
```

---

## 📝 ESTRUCTURA RESUMIDA DE ARCHIVOS

| Tipo | Cantidad | Tamaño aproximado |
|------|----------|-------------------|
| Python (.py) | 18 | ~3,500 líneas |
| HTML (.html) | 36+ | ~4,200 líneas |
| CSS (.css) | 1 | ~500 líneas |
| JavaScript (.js) | 4 | ~1,500 líneas |
| Config/Otras | 4 | - |
| **TOTAL** | **63+** | **~18,000 líneas** |

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Carpetas creadas
- [ ] Archivos Python copiados a models/ y routes/
- [ ] Archivos HTML copiados a templates/
- [ ] Archivos JavaScript copiados a static/js/
- [ ] Archivos raíz (app.py, config.py, etc.) en raíz del proyecto
- [ ] setup.sh ejecutado correctamente
- [ ] venv activado
- [ ] Dependencias instaladas (pip install -r requirements.txt)
- [ ] BD inicializada (python database_init.py)
- [ ] App iniciada (python app.py)
- [ ] Accesible en http://localhost:5000
- [ ] Dashboard visible en http://localhost:5000/dashboard

---

¡Proyecto completamente funcional! 🚀

