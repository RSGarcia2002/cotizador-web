from datetime import datetime, timedelta

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def fecha_guatemala() -> str:
    hoy = datetime.now()
    return f"Guatemala, {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"



def fecha_validez() -> str:
    fecha = datetime.now() + timedelta(days=30)
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"



def fecha_corta_desde_texto(fecha_texto: str) -> str:
    try:
        partes = fecha_texto.replace("Guatemala,", "").strip().split(" de ")
        if len(partes) == 3:
            return f"{partes[1]} de {partes[2]}"
    except Exception:
        pass
    return ""
