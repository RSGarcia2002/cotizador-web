import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)


def subir_pdf(ruta_local, carpeta="cotizador"):
    """Sube un PDF a Cloudinary y retorna la URL pública."""
    resultado = cloudinary.uploader.upload(
        ruta_local,
        folder=carpeta,
        resource_type="raw",  # PDFs son 'raw' en Cloudinary
        use_filename=True,
        unique_filename=True,
    )
    return resultado["secure_url"]


def eliminar_pdf(url_cloudinary):
    """Elimina un archivo de Cloudinary dado su URL."""
    if not url_cloudinary:
        return
    # Extraer el public_id de la URL
    partes = url_cloudinary.split("/upload/")
    if len(partes) < 2:
        return
    public_id_con_ext = partes[1]
    # Quitar versión si existe (v1234567/)
    if public_id_con_ext.startswith("v") and "/" in public_id_con_ext:
        public_id_con_ext = public_id_con_ext.split("/", 1)[1]
    # Quitar extensión
    public_id = public_id_con_ext.rsplit(".", 1)[0]
    cloudinary.uploader.destroy(public_id, resource_type="raw")