import re


def limpiar_numero(valor):
    if not valor:
        return None
    valor = valor.replace(",", "").strip()
    try:
        return float(valor)
    except ValueError:
        return None


def parser_glad_naturalisimo(texto: str):
    resultado = {
        "numero_orden": None,
        "fecha_orden": None,
        "nit": None,
        "condiciones_pago": None,
        "proyecto": None,
        "subtotal": None,
        "iva": None,
        "total": None,
    }

    if not texto:
        return resultado

    m = re.search(r"Orden de Compra\s+(\d+)", texto, re.IGNORECASE)
    if m:
        resultado["numero_orden"] = m.group(1).strip()

    m = re.search(r"Fecha\s+(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
    if m:
        fecha = m.group(1)
        dd, mm, yyyy = fecha.split("/")
        resultado["fecha_orden"] = f"{yyyy}-{mm}-{dd}"

    m = re.search(r"NIT:\s*([0-9\-]+)", texto, re.IGNORECASE)
    if m:
        resultado["nit"] = m.group(1).strip()

    m = re.search(r"Condiciones pago:\s*(.*?)\s+Proyecto", texto, re.IGNORECASE)
    if m:
        resultado["condiciones_pago"] = m.group(1).strip()

    m = re.search(r"Proyecto\s+(.*?)\s+(?:2\.4|Articulo|Artículo)", texto, re.IGNORECASE)
    if m:
        resultado["proyecto"] = m.group(1).strip()

    m = re.search(r"\bSubtotal\s+QTZ\s+([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        resultado["subtotal"] = limpiar_numero(m.group(1))

    m = re.search(r"\bIva\s+QTZ\s+([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        resultado["iva"] = limpiar_numero(m.group(1))

    totales = re.findall(r"\bTotal\s+QTZ\s+([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if totales:
        resultado["total"] = limpiar_numero(totales[-1])

    return resultado

def parser_chocolates_best(texto: str):
    resultado = {
        "numero_orden": None,
        "fecha_orden": None,
        "nit": None,
        "condiciones_pago": None,
        "proyecto": None,
        "subtotal": None,
        "iva": None,
        "total": None,
    }

    if not texto:
        return resultado

    # Pedido / orden
    m = re.search(r"Pedido de compra:\s*(\d+)", texto, re.IGNORECASE)
    if not m:
        m = re.search(r"Pedido de compra\s*\n.*?\n(\d{6,})", texto, re.IGNORECASE | re.DOTALL)
    if m:
        resultado["numero_orden"] = m.group(1).strip()

    # NIT / ID Fiscal del emisor del pedido
    m = re.search(r"ID Fiscal\s*([0-9\-]+)", texto, re.IGNORECASE)
    if m:
        resultado["nit"] = m.group(1).strip()

    # Condiciones de pago
    m = re.search(r"Condiciones de pago\s*(.*?)\s*(?:Comentarios|Otra información)", texto, re.IGNORECASE | re.DOTALL)
    if m:
        resultado["condiciones_pago"] = " ".join(m.group(1).split()).strip()

    # Subtotal
    m = re.search(r"Subtotal:\s*Q\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        resultado["subtotal"] = limpiar_numero(m.group(1))

    # IVA / impuestos
    m = re.search(r"Total estimado de impuestos:\s*Q\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        resultado["iva"] = limpiar_numero(m.group(1))

    # Total
    m = re.search(r"Suma total estimada:\s*Q\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if m:
        resultado["total"] = limpiar_numero(m.group(1))

    # Descripción / proyecto
    m = re.search(r"RECIPIENTE PARA LODOS", texto, re.IGNORECASE)
    if m:
        resultado["proyecto"] = "RECIPIENTE PARA LODOS"
    else:
        m = re.search(r"\n\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{6,})\s*\n\s*ESTADO", texto, re.IGNORECASE)
        if m:
            resultado["proyecto"] = " ".join(m.group(1).split()).strip()

    # Fecha requerida / fecha orden aproximada
    # Caso: "Need-by Date: mié, 25 mar, 2026"
    meses = {
        "ene": "01", "feb": "02", "mar": "03", "abr": "04",
        "may": "05", "jun": "06", "jul": "07", "ago": "08",
        "sep": "09", "oct": "10", "nov": "11", "dic": "12"
    }

    m = re.search(r"Need-by Date:\s*.*?(\d{1,2})\s+([a-záéíóú]{3}),\s*(\d{4})", texto, re.IGNORECASE)
    if m:
        dia = m.group(1).zfill(2)
        mes_txt = m.group(2).lower()[:3]
        anio = m.group(3)
        mes = meses.get(mes_txt)
        if mes:
            resultado["fecha_orden"] = f"{anio}-{mes}-{dia}"
    else:
        # Caso alterno: "25 Mar 2026 07:00:00 GMT"
        m = re.search(r"Fecha para la que se requiere:\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", texto, re.IGNORECASE)
        if m:
            dia = m.group(1).zfill(2)
            mes_txt = m.group(2).lower()[:3]
            anio = m.group(3)
            mes = meses.get(mes_txt)
            if mes:
                resultado["fecha_orden"] = f"{anio}-{mes}-{dia}"

    return resultado

def parser_cda(texto: str):
    resultado = {
        "numero_orden": None,
        "fecha_orden": None,
        "nit": None,
        "condiciones_pago": None,
        "proyecto": None,
        "subtotal": None,
        "iva": None,
        "total": None,
    }

    if not texto:
        return resultado

    # Número de orden
    m = re.search(r"ORDEN DE COMPRA No\.\s*([A-Z0-9\-]+)", texto, re.IGNORECASE)
    if m:
        resultado["numero_orden"] = m.group(1).strip()

    # Fecha
    m = re.search(r"Fecha:\s*(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
    if m:
        fecha = m.group(1)
        dd, mm, yyyy = fecha.split("/")
        resultado["fecha_orden"] = f"{yyyy}-{mm}-{dd}"

    # NIT del cliente
    m = re.search(r"COLEGIO DECROLY AMERICANO\s+NIT\.?\s*([0-9\-]+)", texto, re.IGNORECASE)
    if m:
        resultado["nit"] = m.group(1).strip()

    # Proyecto / cuenta por afectar
    m = re.search(
        r"Cuenta por afectar:\s*\[?\s*(.*?)\s*(?:Vo\.Bo,|Vo\.Bo\.|Vo\.Bo|CONTROL INTERNO)",
        texto,
        re.IGNORECASE | re.DOTALL
    )
    if m:
        proyecto = m.group(1).strip()
        proyecto = proyecto.split("Vo.Bo")[0].strip()
        proyecto = " ".join(proyecto.split()).strip(" ]")
        if proyecto:
            resultado["proyecto"] = proyecto

    if not resultado["proyecto"]:
        m = re.search(
            r"ASUNTO:\s*(.*?)\s*(?:PRECIOS:|TIEMPO DE ENTREGA:|VALIDEZ:)",
            texto,
            re.IGNORECASE | re.DOTALL
        )
        if m:
            proyecto = " ".join(m.group(1).split()).strip()
            if proyecto:
                resultado["proyecto"] = proyecto

    # Total
    totales = re.findall(r"Total\s+[¡i]?\s*a?\s*Q?\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)
    if not totales:
        totales = re.findall(r"TOTAL\s+Q\s*([\d,]+\.\d{2})", texto, re.IGNORECASE)

    if totales:
        total_val = limpiar_numero(totales[-1])
        resultado["total"] = total_val
        resultado["subtotal"] = total_val
        resultado["iva"] = 0.0

    # Condiciones de pago
    m = re.search(
        r"DIAS DE CREDITO\.?\s*(.*?)(?:CUENTA BANCARIA|NOMBRE DEL BANCO|FORMA DE PAGO)",
        texto,
        re.IGNORECASE | re.DOTALL
    )
    if m:
        condiciones = " ".join(m.group(1).split()).strip(" |")
        if condiciones and len(condiciones) < 120:
            resultado["condiciones_pago"] = condiciones

    return resultado

def parsear_orden_por_plantilla(plantilla_ocr: str, texto: str):
    plantilla = (plantilla_ocr or "").strip().lower()

    if plantilla in ("glad_naturalisimo", "naturalisimo", "glad"):
        return parser_glad_naturalisimo(texto)

    if plantilla in ("chocolates_best", "chocolates", "best"):
        return parser_chocolates_best(texto)

    if plantilla in ("cda", "decroly", "colegio_decroly"):
        return parser_cda(texto)

    return {}
