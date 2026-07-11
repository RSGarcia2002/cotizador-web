# Cotizador Web

Aplicacion web para administrar cotizaciones, ordenes de compra y facturas de
Multiservicios Siney. El sistema centraliza el flujo comercial: crea
cotizaciones en PDF, conserva historial, gestiona catalogos, registra ordenes y
permite asociar documentos de soporte.

## Funcionalidades principales

- Generacion de cotizaciones con correlativo anual y exportacion a PDF.
- Historial de cotizaciones con estados, duplicado, edicion y eliminacion.
- Catalogos de empresas, ingenieros y asuntos para agilizar formularios.
- Gestion de ordenes de compra y registro de facturas asociadas.
- Carga de archivos PDF y almacenamiento local o en Cloudinary.
- Extraccion de datos desde PDFs de ordenes y facturas mediante OCR/parsers.
- Autenticacion con Flask-Login y proteccion CSRF en formularios.

## Tecnologias

- Python
- Flask
- PostgreSQL
- Flask-Login
- WeasyPrint
- OpenPyXL
- PyMuPDF / Tesseract OCR
- Cloudinary
- HTML, CSS y plantillas Jinja

## Estructura

```text
app.py                  Punto de entrada de Flask
db.py                   Conexion y helpers de base de datos
init_db.py              Inicializacion de tablas/configuracion
routes/                 Rutas web y autenticacion
services/               Logica de negocio, OCR, catalogos y almacenamiento
templates/              Vistas HTML y plantilla de PDF
static/css/             Estilos visuales
uploads/                Documentos cargados durante la operacion
```

## Configuracion

El proyecto usa variables de entorno. Como minimo se requiere:

```bash
SECRET_KEY=clave-segura
DATABASE_URL=postgresql://usuario:password@host:puerto/base
```

Si se usa Cloudinary para almacenar PDFs, tambien se deben configurar las
credenciales correspondientes segun el servicio.

## Instalacion local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecucion

```bash
flask --app app run --debug
```

Tambien se puede ejecutar directamente:

```bash
python app.py
```

La aplicacion inicializa la conexion a base de datos y crea las carpetas de
carga necesarias para ordenes y facturas.

## Notas

El repositorio incluye archivos de prueba y cargas de ejemplo para validar la
extraccion de informacion desde PDFs. En un entorno productivo conviene mover
los archivos sensibles o generados a almacenamiento externo y mantenerlos fuera
del control de versiones.
