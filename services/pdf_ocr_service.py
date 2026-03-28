import os
import re
from pypdf import PdfReader
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


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
    Devuelve:
    {
        'texto': str,
        'metodo': 'pdf' | 'ocr' | 'vacio'
    }
    """
    texto_directo = extraer_texto_pdf_directo(ruta_pdf)

    # si ya encontró suficiente texto, usamos ese
    if texto_directo and len(texto_directo.strip()) > 50:
        return {
            "texto": texto_directo,
            "metodo": "pdf",
        }

    texto_ocr = extraer_texto_pdf_ocr(ruta_pdf)
    if texto_ocr and len(texto_ocr.strip()) > 20:
        return {
            "texto": texto_ocr,
            "metodo": "ocr",
        }

    return {
        "texto": "",
        "metodo": "vacio",
    }