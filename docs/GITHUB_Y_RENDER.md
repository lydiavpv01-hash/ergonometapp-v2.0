# 🚀 ERGONOMETAPP V2.0 EN GITHUB Y RENDER

**Guía paso-a-paso para subir tu proyecto a GitHub y correrlo en Render**

---

## PARTE 1: PREPARAR PROYECTO PARA GITHUB

### Paso 1.1: Crear repositorio local

```bash
# Navega a tu carpeta del proyecto
cd ~/tu-ruta/ergonometapp-v2.0

# Verificar que tienes estos archivos
ls -la | grep -E "app.py|config.py|requirements.txt|Procfile|runtime.txt"

# Deberías ver:
# ✅ app.py
# ✅ config.py
# ✅ requirements.txt
# ✅ Procfile
# ✅ runtime.txt
# ✅ .gitignore
```

### Paso 1.2: Inicializar Git

```bash
# Inicializar repositorio
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Initial commit: ErgonometApp v2.0"

# Ver archivos (no debería ver venv/ ni __pycache__)
git status
```

---

## PARTE 2: CREAR REPOSITORIO EN GITHUB

### Paso 2.1: En GitHub.com

1. Ve a https://github.com/new
2. Crea repositorio con nombre: `ergonometapp-v2.0`
3. **NO inicialices con README** (ya tienes uno)
4. Copia el URL (ej: https://github.com/tu-usuario/ergonometapp-v2.0.git)

### Paso 2.2: Conectar local con GitHub

```bash
# Agregar remoto
git remote add origin https://github.com/tu-usuario/ergonometapp-v2.0.git

# Renombrar rama a main
git branch -M main

# Subir código
git push -u origin main
```

**Verifica:** Abre https://github.com/tu-usuario/ergonometapp-v2.0 en navegador
Deberías ver todos tus archivos ✅

---

## PARTE 3: CONFIGURAR RENDER

### Paso 3.1: Crear cuenta en Render

1. Ve a https://render.com
2. Haz clic en "Sign up"
3. Conéctate con GitHub (elige autorizar)

### Paso 3.2: Crear Web Service

1. En Render dashboard, haz clic: **"New +"**
2. Elige: **"Web Service"**
3. Haz clic: **"Connect a repository"**
4. Busca: `ergonometapp-v2.0`
5. Haz clic: **"Connect"**

### Paso 3.3: Configurar servicio

**Nombre:** (ej: `ergonometapp-v2-0`)

**Environment:** Python 3

**Region:** Elige la más cercana a ti (o Default)

**Build Command:**
```
pip install -r requirements.txt && python database_init.py
```

**Start Command:**
```
gunicorn app:app
```

### Paso 3.4: Agregar variables de entorno

Haz clic en **"Environment"** y agrega:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `tu-clave-muy-larga-y-segura-aqui-cambiar` |
| `PYTHON_VERSION` | `3.11.6` |

**Para SECRET_KEY, usa algo como:**
```
openssl rand -hex 32
# Resultado: e8f5g3h2i9j4k1l6m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f6g7h8
```

### Paso 3.5: Deploy

Haz clic en: **"Deploy"**

**Espera 2-5 minutos mientras Render:**
- ✅ Clona tu repositorio
- ✅ Instala dependencias
- ✅ Crea base de datos
- ✅ Inicia servidor

---

## PARTE 4: VERIFICAR QUE FUNCIONA

### En Render

1. Espera a que veas: **"Your service is live"**
2. Tu URL será algo como: `https://ergonometapp-v2-0.onrender.com`
3. Haz clic y abre en navegador

**Deberías ver:**
```
✅ http://ergonometapp-v2-0.onrender.com/ → Página principal
✅ http://ergonometapp-v2-0.onrender.com/dashboard → Dashboard
✅ http://ergonometapp-v2-0.onrender.com/reba/nueva → Crear evaluación
```

### Logs en Render

Si algo falla:
1. Vuelve a Render dashboard
2. Tu servicio → **"Logs"**
3. Lee los errores (abajo)
4. Soluciona y haz `git push` (redeploy automático)

---

## PARTE 5: ACTUALIZACIONES FUTURAS

### Cada vez que hagas cambios:

```bash
# Editar archivos localmente
# (ej: cambiar config, agregar métodos, etc)

# Subir a GitHub
git add .
git commit -m "Descripción de cambios"
git push origin main

# Render redeploy automático (espera ~2-5 min)
# Verifica en: Render dashboard
```

---

## ⚠️ TROUBLESHOOTING

### Error: "Build failed"

**Problema:** Errores en instalación de dependencias

**Solución:**
1. Verifica `requirements.txt` está correcto
2. Intenta instalar localmente: `pip install -r requirements.txt`
3. Haz `git push` nuevamente

### Error: "Application failed to start"

**Problema:** Error en `app.py` o `config.py`

**Solución:**
1. Mira **Logs** en Render
2. Lee el error (última línea)
3. Arregla localmente
4. `git push` nuevamente

### Error: "Cannot find module"

**Problema:** Faltan archivos o estructura incorrecta

**Solución:**
```bash
# Verifica estructura local
ls models/
ls routes/
ls templates/

# Los archivos __init__.py existen?
ls models/__init__.py
ls routes/__init__.py
ls routes/metodos/__init__.py

# Si falta algo, créalo:
touch models/__init__.py
git add . && git commit -m "Fix: add missing __init__.py"
git push
```

### Error: "Database locked"

**Problema:** SQLite tiene conflictos en servidor

**Solución:**
1. Render ya maneja esto, pero si persiste:
2. En Render, haz clic: **"Manual Deploy"**
3. Espera a que se complete

### El dashboard no carga datos

**Problema:** BD vacía o falta inicialización

**Solución:**
```bash
# Localmente, recrea BD
rm database/ergonometapp.db
python database_init.py

# En Render irá más limpio
# (se ejecuta: python database_init.py en Build Command)
```

---

## 📊 CHECKLIST FINAL

### Antes de producción

- [ ] Código en GitHub
- [ ] Archivo `Procfile` presente
- [ ] Archivo `runtime.txt` con Python 3.11
- [ ] `requirements.txt` actualizado (con gunicorn)
- [ ] Variables de entorno en Render configuradas
- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY` seguro (sin espacios, 32+ caracteres)
- [ ] `.gitignore` configrado (sin venv/ ni database/)
- [ ] BD inicializada (`python database_init.py` en build)
- [ ] Logs sin errores en Render
- [ ] App accesible en navegador ✅

---

## 🔗 URLS IMPORTANTES

```
Repositorio GitHub
→ https://github.com/tu-usuario/ergonometapp-v2.0

Render Dashboard
→ https://dashboard.render.com

Tu app en Render
→ https://ergonometapp-v2-0.onrender.com

(Nota: reemplaza "tu-usuario" y "ergonometapp-v2-0" con los tuyos)
```

---

## 💡 TIPS

1. **Redeploy rápido sin cambios:** En Render → "Manual Deploy" → "Deploy latest commit"

2. **Ver logs en tiempo real:**
   ```bash
   # En Render, haz clic en "Logs" y ves en vivo
   ```

3. **Cambiar SECRET_KEY:** En Render → Environment → editar → guardar (redeploy)

4. **Migrar de Render:** Descarga respaldos, mantén GitHub como fuente

5. **Dominio personalizado:** En Render → Settings → agregar dominio (Ej: evalergo.com)

---

## 📞 SOPORTE RENDER

- Docs: https://render.com/docs
- Status: https://status.render.com
- Chat: https://render.com/support (en dashboard)

---

## 🎉 ¡LISTO!

Tu app está en internet, visible para todo el mundo.

**Próximos pasos:**
1. Comparte el URL: https://ergonometapp-v2-0.onrender.com
2. Haz cambios locales
3. `git push` para actualizar en vivo
4. ¡Disfruta!

---

**ErgonometApp v2.0 - En GitHub y Render**  
Actualizado: 31 de agosto de 2026

🚀 Tu app en producción
