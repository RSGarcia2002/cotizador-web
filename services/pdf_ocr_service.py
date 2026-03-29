import os
import re
from pypdf import PdfReader
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import tempfile
import urllib.request


def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.replace("\x00", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{2,}", "\n\n", texto)
    return texto.strip()


def extraer_texto_pdf_directo(ruta_pdf: str) -> str:
    try:
        reader = PdfReader(ruta_pdf)
        partes = []
        for page in reader.pages:
            partes.append(page.extract_text() or "")
        return limpiar_texto("\n".join(partes))
    except Exception:
        return ""


def extraer_texto_pdf_ocr(ruta_pdf: str) -> str:
    try:
        doc = fitz.open(ruta_pdf)
        partes = []

        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            texto = pytesseract.image_to_string(img, lang="spa")
            if texto:
                partes.append(texto)

        return limpiar_texto("\n".join(partes))
    except Exception:
        return ""


def extraer_texto_pdf(ruta_pdf: str):
    """
    Acepta tanto rutas locales como URLs de Cloudinary.
    Devuelve:
    {
        'texto': str,
        'metodo': 'pdf' | 'ocr' | 'vacio'
    }
    """
    # Si es una URL, descargar a archivo temporal
    archivo_temp = None
    if ruta_pdf.startswith("http://") or ruta_pdf.startswith("https://"):
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            urllib.request.urlretrieve(ruta_pdf, tmp.name)
            archivo_temp = tmp.name
            ruta_pdf = tmp.name
        except Exception:
            return {"texto": "", "metodo": "vacio"}

    try:
        texto_directo = extraer_texto_pdf_directo(ruta_pdf)
        if texto_directo and len(texto_directo.strip()) > 50:
            return {"texto": texto_directo, "metodo": "pdf"}

        texto_ocr = extraer_texto_pdf_ocr(ruta_pdf)
        if texto_ocr and len(texto_ocr.strip()) > 20:
            return {"texto": texto_ocr, "metodo": "ocr"}

        return {"texto": "", "metodo": "vacio"}
    finally:
        # Borrar archivo temporal si se creó
        if archivo_temp and os.path.exists(archivo_temp):
            os.remove(archivo_temp)