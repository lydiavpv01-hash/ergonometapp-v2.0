# ErgonometApp v2.0 🚀

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Flask 2.3.3](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/database-sqlite-lightgrey.svg)](https://www.sqlite.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Aplicación web profesional para **evaluación ergonómica** según normas mexicanas (SEMARNAT, STPS). Implementa 6 métodos de evaluación con dashboard analítico, gráficos interactivos y reportes.

## 📊 Características

### ✅ 6 Métodos Ergonómicos Implementados

| Método | Pasos | Descripción |
|--------|-------|-------------|
| **REBA** | 5 | Rapid Entire Body Assessment |
| **Ley SILLA** | 3 | Evaluación de Bipedestación |
| **LEST** | 4 | List of Ergonomic Tasks |
| **Apéndice I** | 3 | Levantamiento de Cargas (Fórmula ACGIH) |
| **Apéndice II** | 3 | Empuje y Arrastre |
| **Cuestionario Nórdico** | 2 | Síntomas Musculoesqueléticos |

### 📈 Dashboard Profesional

- 📊 Gráficos interactivos (Chart.js)
- 🎯 Análisis de riesgos en tiempo real
- 📅 Filtros por fecha, trabajador, método
- 📥 Exportación a PDF y Excel
- 📋 Histórico de evaluaciones

### 💾 Características Técnicas

- ✅ Base de datos SQLite con 7 tablas
- ✅ ORM con SQLAlchemy
- ✅ Arquitectura modular (Blueprints)
- ✅ Validación client/server
- ✅ Generación automática de reportes
- ✅ Responsive design (móvil + desktop)

---

## 🚀 Instalación Local

### Requisitos
- Python 3.8+
- pip
- 100 MB espacio libre

### Pasos rápidos

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/ergonometapp-v2.0.git
cd ergonometapp-v2.0

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar BD
python database_init.py

# 5. Ejecutar
python app.py
```

Abre: http://localhost:5000

---

## 🌐 Deploy en Render

### Paso 1: Preparar repositorio

```bash
# Asegúrate que tienes:
# ✅ requirements.txt
# ✅ Procfile
# ✅ runtime.txt
# ✅ .gitignore

git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Paso 2: Conectar con Render

1. Ve a https://render.com
2. Crea una nueva cuenta (o inicia sesión)
3. **Crear Web Service:**
   - **Repository:** tu-repo-github
   - **Branch:** main
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python database_init.py`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:**
     ```
     FLASK_ENV=production
     SECRET_KEY=tu-clave-secreta-super-larga
     ```

### Paso 3: Deploy automático

```bash
git push origin main  # Deploy automático ✨
```

**Tu app estará en:** https://tu-app-name.onrender.com

---

## 📁 Estructura del Proyecto

```
ergonometapp-v2.0/
├── app.py                      # Aplicación principal
├── config.py                   # Configuración
├── requirements.txt            # Dependencias
├── Procfile                    # Para Render
├── runtime.txt                 # Versión Python
│
├── models/
│   ├── __init__.py
│   ├── calculadores.py         # REBA
│   ├── ley_silla.py
│   ├── lest.py
│   ├── apendice_i.py
│   ├── apendice_ii.py
│   └── kuorinka.py
│
├── routes/
│   ├── __init__.py
│   ├── main.py
│   ├── dashboard.py
│   └── metodos/
│       ├── __init__.py
│       ├── reba.py
│       ├── ley_silla.py
│       ├── lest.py
│       ├── apendice_i.py
│       ├── apendice_ii.py
│       └── kuorinka.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── metodos/
│       ├── reba/
│       ├── ley_silla/
│       ├── lest/
│       ├── apendice_i/
│       ├── apendice_ii/
│       └── kuorinka/
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── charts.js
│   │   ├── dashboard.js
│   │   └── kinovea.js
│   └── images/
│
├── database/
│   └── ergonometapp.db         # SQLite (creada automáticamente)
│
└── .env.example                 # Variables de entorno (copiar a .env)
```

---

## 📝 Endpoints Principales

### Rutas Principales
```
GET  /                          Página principal
GET  /metodos                   Listar métodos
GET  /trabajadores              Gestión de trabajadores
GET  /dashboard                 Dashboard
```

### Métodos Ergonómicos
```
GET  /reba/nueva
GET  /ley-silla/nueva
GET  /lest/nueva
GET  /apendice-i/nueva
GET  /apendice-ii/nueva
GET  /cuestionario-nordico/nueva
```

### API Dashboard
```
GET  /dashboard/api/datos              Datos en JSON
GET  /dashboard/exportar/pdf           Exportar PDF
GET  /dashboard/exportar/excel         Exportar Excel
```

---

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y personaliza:

```bash
cp .env.example .env
```

```ini
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=tu-clave-super-segura
DATABASE_URL=sqlite:///database/ergonometapp.db
```

### Modo Desarrollo

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

---

## 📊 Base de Datos

### Tablas principales

```sql
-- Usuarios del sistema
usuarios (id, nombre, email, password, rol)

-- Trabajadores evaluados
trabajadores (id, nombre, puesto, departamento, edad)

-- Evaluaciones (registro principal)
evaluaciones (id, trabajador_id, metodo, resultado)

-- Resultados por método
resultados_reba
resultados_ley_silla
resultados_lest
resultados_apendice_i
resultados_apendice_ii
resultados_kuorinka
```

### Inicializar BD

```bash
python database_init.py
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
```bash
python app.py --port 5001
```

### Error: "Database locked"
```bash
rm database/ergonometapp.db
python database_init.py
```

### En Render: Error de imports
- Asegúrate que `__init__.py` existe en:
  - `models/`
  - `routes/`
  - `routes/metodos/`

---

## 📚 Documentación Técnica

- [ARQUITECTURA.md](docs/ARQUITECTURA.md) - Diseño del proyecto
- [METODOS.md](docs/METODOS.md) - Detalles de cálculos
- [API.md](docs/API.md) - Documentación de endpoints
- [DATABASE.md](docs/DATABASE.md) - Schema de BD

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles

---

## 👥 Autor

**Ing. Lydia Peralta**  
Conciencia Verde y Laboral S.C.  
📧 lydia@concienciaverde.com.mx

---

## 🌟 Estadísticas

- **Líneas de código:** ~18,000
- **Métodos implementados:** 6/6
- **Archivos:** 65+
- **Funciones:** 80+
- **Templates:** 36+

---

## 📞 Soporte

¿Preguntas o problemas?

1. Revisa [Troubleshooting](#-troubleshooting)
2. Abre un [Issue](https://github.com/tu-usuario/ergonometapp-v2.0/issues)
3. Contacta: lydia@concienciaverde.com.mx

---

## 🎯 Roadmap

- [x] 6 métodos ergonómicos
- [x] Dashboard profesional
- [x] Base de datos integrada
- [x] Exportación PDF/Excel
- [ ] Autenticación de usuarios
- [ ] Análisis comparativo
- [ ] Móvil app nativa
- [ ] Integración con sistemas existentes

---

**ErgonometApp v2.0** - Evaluación Ergonómica Profesional  
Actualizado: 31 de agosto de 2026

⭐ Si te fue útil, dale una estrella en GitHub
