# AI Podcast Tracker 🎙️

Sistema profesional para rastrear automáticamente nuevos episodios de podcasts españoles de Inteligencia Artificial.

## 🚀 Características

- ✅ **Rastreo Automático**: Chequeo periódico de nuevos episodios cada hora
- ✅ **Base de Datos SQLite**: Almacenamiento persistente de podcasts y episodios
- ✅ **API REST con FastAPI**: Backend moderno y rápido
- ✅ **Interfaz Web Premium**: Diseño moderno con dark mode y glassmorphism
- ✅ **Tests Completos**: Cobertura de código con pytest (80%+)
- ✅ **Estructura Profesional**: Organización clara y escalable

## 📋 Requisitos

- Python 3.9+
- pip o Poetry

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
cd podcast-tracker
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)

```bash
cp .env.example .env
# Editar .env según necesidades
```

## 🎯 Uso

### Iniciar la aplicación

```bash
cd src
python -m podcast_tracker.main
```

La aplicación estará disponible en: http://localhost:8000

### Acceder a la documentación de la API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Tests

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=src/podcast_tracker --cov-report=html
```

### Ejecutar solo tests unitarios

```bash
pytest tests/unit/ -m unit
```

### Ejecutar solo tests de integración

```bash
pytest tests/integration/ -m integration
```

## 📁 Estructura del Proyecto

```
podcast-tracker/
├── src/
│   └── podcast_tracker/
│       ├── api/              # Endpoints de FastAPI
│       ├── database/         # Modelos y configuración de DB
│       ├── services/         # Lógica de negocio
│       ├── static/           # Frontend (HTML/CSS/JS)
│       ├── config.py         # Configuración
│       └── main.py           # Entry point
├── tests/
│   ├── unit/                 # Tests unitarios
│   └── integration/          # Tests de integración
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🎨 Funcionalidades de la Interfaz

- **Dashboard**: Vista general de podcasts y episodios pendientes
- **Filtros**: Filtrar episodios por podcast
- **Paginación**: Navegación eficiente de episodios
- **Marcar como escuchado**: Gestión de episodios
- **Actualización manual**: Botón para forzar actualización
- **Auto-refresh**: Actualización automática cada 5 minutos
- **Enlaces directos**: Acceso rápido a Spotify

## 🔧 Configuración

Variables de entorno disponibles en `.env`:

```env
DATABASE_URL=sqlite:///./podcast_tracker.db
CHECK_INTERVAL_HOURS=1
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## 📡 API Endpoints

- `GET /api/podcasts` - Listar todos los podcasts
- `GET /api/episodes` - Listar episodios pendientes (con paginación)
- `GET /api/episodes/{id}` - Obtener episodio específico
- `PATCH /api/episodes/{id}/listened` - Marcar como escuchado
- `POST /api/podcasts/refresh` - Forzar actualización manual

## 🎙️ Podcasts Incluidos

1. **Loop Infinito** (by Xataka)
2. **El Test de Turing**
3. **Inteligencia Artificial** con Jon Hernandez
4. **Inteligencia Artificial** - Pocho Costa

## 🔄 Scheduler

El sistema incluye un scheduler que:
- Se ejecuta cada hora (configurable)
- Chequea nuevos episodios en todos los podcasts
- Añade automáticamente episodios nuevos a la base de datos
- Registra toda la actividad en logs

## 🐛 Troubleshooting

### La aplicación no inicia

```bash
# Verificar que las dependencias estén instaladas
pip install -r requirements.txt

# Verificar que el puerto 8000 esté libre
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac
```

### No se detectan nuevos episodios

- Verificar que los RSS feeds sean válidos
- Revisar los logs para errores
- Forzar actualización manual desde la interfaz

## 📝 Licencia

MIT License

## 👨‍💻 Desarrollo

### Agregar un nuevo podcast

Editar `src/podcast_tracker/main.py` y añadir a `INITIAL_PODCASTS`:

```python
{
    "name": "Nombre del Podcast",
    "rss_url": "https://example.com/feed.xml",
    "spotify_url": "https://open.spotify.com/show/..."
}
```

### Modificar intervalo de chequeo

Editar `.env`:

```env
CHECK_INTERVAL_HOURS=2  # Chequear cada 2 horas
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Hecho con ❤️ para la comunidad de IA en español**
