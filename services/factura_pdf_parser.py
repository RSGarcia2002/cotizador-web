import re


def limpiar_numero(valor):
    if not valor:
        return None
    valor = valor.replace(",", "").strip()
    try:
        return float(valor)
    except ValueError:
        return None


def parsear_factura_sat(texto: str):
    resultado = {
        "numero_factura": None,
        "serie_factura": None,
        "fecha_factura": None,
        "monto_facturado": None,
    }

    if not texto:
        return resultado

    m = re.search(r"Serie:\s*([A-Z0-9]+)", texto, re.IGNORECASE)
    if m:
        resultado["serie_factura"] = m.group(1).strip()

    m = re.search(r"N[uú]mero de DTE:\s*([0-9]+)", texto, re.IGNORECASE)
    if m:
        resultado["numero_factura"] = m.group(1).strip()

    m = re.search(
        r"Fecha y hora de emisi[oó]n:\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})",
        texto,
        re.IGNORECASE,
    )
    if m:
        dia = m.group(1).zfill(2)
        mes_txt = m.group(2).lower()
        anio = m.group(3)

        meses = {
            "ene": "01", "feb": "02", "mar": "03", "abr": "04",
            "may": "05", "jun": "06", "jul": "07", "ago": "08",
            "sep": "09", "oct": "10", "nov": "11", "dic": "12"
        }
        mes = meses.get(mes_txt[:3])
        if mes:
            resultado["fecha_factura"] = f"{anio}-{mes}-{dia}"

    m = re.search(r"TOTALES:\s*GTQ\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        resultado["monto_facturado"] = limpiar_numero(m.group(1))

    return resultado