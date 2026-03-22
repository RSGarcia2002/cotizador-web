# Refactor sugerido

## Estructura
- `app.py`: arranque de Flask
- `db.py`: pool de conexiones a PostgreSQL
- `init_db.py`: creación de tablas y seed
- `routes/main.py`: rutas
- `services/catalog_service.py`: lógica de catálogos
- `services/cotizacion_service.py`: lógica de cotizaciones
- `services/helpers.py`: fechas y helpers

## Mejora de rendimiento más importante
Se cambió de abrir una conexión nueva en casi cada función a usar `SimpleConnectionPool` de psycopg2.

Eso normalmente reduce mucho la lentitud cuando la app está en Render/Postgres porque evita:
- abrir/cerrar conexión por cada consulta
- múltiples handshakes por request
- latencia extra innecesaria

## Cómo probar
```bash
source .venv/bin/activate
export DATABASE_URL="tu_url"
python3 app.py
```
