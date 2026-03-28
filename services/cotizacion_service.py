from datetime import datetime
from urllib.parse import urlencode
from db import fetch_all, fetch_one, execute, execute_returning_one
from services.helpers import fecha_corta_desde_texto


def obtener_no_referencia():
    anio = datetime.now().year
    row = fetch_one("SELECT valor FROM configuracion WHERE clave = %s", ("correlativo",))
    correlativo = int(row["valor"]) if row else 1
    return f"NT-{anio}-{correlativo:04d}"



def incrementar_correlativo():
    row = fetch_one("SELECT valor FROM configuracion WHERE clave = %s", ("correlativo",))
    correlativo = int(row["valor"]) if row else 1
    correlativo += 1
    execute(
        """
        INSERT INTO configuracion (clave, valor)
        VALUES (%s, %s)
        ON CONFLICT (clave)
        DO UPDATE SET valor = EXCLUDED.valor
        """,
        ("correlativo", str(correlativo)),
    )



def crear_cotizacion(data: dict):
    execute(
        """
        INSERT INTO cotizaciones (
            no_referencia, fecha, empresa, ingeniero, asunto,
            total_numero, total_letras, estado, pdf_nombre,
            su_referencia, precio_texto, tiempo_entrega, validez,
            encargado, contacto_nombre, contacto_telefono,
            contacto_correo, filas_html, items_json
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.get("no_referencia", ""),
            data.get("fecha", ""),
            data.get("empresa", ""),
            data.get("ingeniero", ""),
            data.get("asunto", ""),
            float(data.get("total_numero", 0) or 0),
            data.get("total_letras", ""),
            "Pendiente",
            f"{data.get('no_referencia', 'cotizacion')}.pdf",
            data.get("su_referencia", ""),
            data.get("precio_texto", ""),
            data.get("tiempo_entrega", ""),
            data.get("validez", ""),
            data.get("encargado", ""),
            data.get("contacto_nombre", ""),
            data.get("contacto_telefono", ""),
            data.get("contacto_correo", ""),
            data.get("filas_html", ""),
            data.get("items_json", ""),
        ),
    )



def listar_cotizaciones():
    cotizaciones = fetch_all(
        """
        SELECT id, no_referencia, fecha, empresa, ingeniero, asunto,
               total_numero, estado, filas_html, items_json
        FROM cotizaciones
        ORDER BY id DESC
        """
    )
    total_aprobadas = fetch_one(
        """
        SELECT COALESCE(SUM(total_numero), 0) AS total
        FROM cotizaciones
        WHERE estado = %s
        """,
        ("Aprobada",),
    )
    return cotizaciones, total_aprobadas["total"]



def obtener_cotizacion(cotizacion_id: int):
    return fetch_one("SELECT * FROM cotizaciones WHERE id = %s", (cotizacion_id,))



def actualizar_estado(cotizacion_id: int, estado: str):
    execute("UPDATE cotizaciones SET estado = %s WHERE id = %s", (estado, cotizacion_id))



def actualizar_cotizacion(data: dict):
    execute(
        """
        UPDATE cotizaciones
        SET empresa = %s,
            ingeniero = %s,
            su_referencia = %s,
            asunto = %s,
            precio_texto = %s,
            tiempo_entrega = %s,
            validez = %s,
            encargado = %s,
            contacto_nombre = %s,
            contacto_telefono = %s,
            contacto_correo = %s,
            filas_html = %s,
            items_json = %s,
            total_numero = %s,
            total_letras = %s,
            fecha = %s
        WHERE id = %s
        """,
        (
            data.get("empresa", ""),
            data.get("ingeniero", ""),
            data.get("su_referencia", ""),
            data.get("asunto", ""),
            data.get("precio_texto", ""),
            data.get("tiempo_entrega", ""),
            data.get("validez", ""),
            data.get("encargado", ""),
            data.get("contacto_nombre", ""),
            data.get("contacto_telefono", ""),
            data.get("contacto_correo", ""),
            data.get("filas_html", ""),
            data.get("items_json", ""),
            float(data.get("total_numero", 0) or 0),
            data.get("total_letras", ""),
            data.get("fecha", ""),
            data.get("cotizacion_id"),
        ),
    )



def eliminar_cotizacion(cotizacion_id: int):
    execute("DELETE FROM cotizaciones WHERE id = %s", (cotizacion_id,))



def construir_params_duplicado(c):
    return urlencode({
        "empresa": c["empresa"] or "",
        "ingeniero": c["ingeniero"] or "",
        "su_referencia": c["su_referencia"] or "",
        "asunto": c["asunto"] or "",
        "encargado": c["encargado"] or "",
        "contacto_nombre": c["contacto_nombre"] or "",
        "contacto_telefono": c["contacto_telefono"] or "",
        "contacto_correo": c["contacto_correo"] or "",
        "items_json": c["items_json"] or "[]",
    })



def construir_params_edicion(c):
    return urlencode({
        "id": c["id"],
        "modo_edicion": "1",
        "empresa": c["empresa"] or "",
        "ingeniero": c["ingeniero"] or "",
        "su_referencia": c["su_referencia"] or "",
        "asunto": c["asunto"] or "",
        "encargado": c["encargado"] or "",
        "contacto_nombre": c["contacto_nombre"] or "",
        "contacto_telefono": c["contacto_telefono"] or "",
        "contacto_correo": c["contacto_correo"] or "",
        "items_json": c["items_json"] or "[]",
        "precio_texto": c["precio_texto"] or "Se entienden netos en Quetzales",
        "tiempo_entrega": c["tiempo_entrega"] or "Inmediata",
        "validez": c["validez"] or "",
        "no_referencia": c["no_referencia"] or "",
        "fecha": c["fecha"] or "",
    })



def preparar_data_pdf(cotizacion: dict):
    return {
        "fecha": cotizacion["fecha"],
        "fecha_corta": fecha_corta_desde_texto(cotizacion["fecha"]),
        "empresa": cotizacion["empresa"],
        "ingeniero": cotizacion["ingeniero"],
        "su_referencia": cotizacion["su_referencia"],
        "no_referencia": cotizacion["no_referencia"],
        "asunto": cotizacion["asunto"],
        "precio_texto": cotizacion["precio_texto"],
        "tiempo_entrega": cotizacion["tiempo_entrega"],
        "validez": cotizacion["validez"],
        "encargado": cotizacion["encargado"],
        "filas_html": cotizacion["filas_html"],
        "total_numero": f"{cotizacion['total_numero']:,.2f}",
        "total_letras": cotizacion["total_letras"],
        "contacto_nombre": cotizacion["contacto_nombre"],
        "contacto_telefono": cotizacion["contacto_telefono"],
        "contacto_correo": cotizacion["contacto_correo"],
    }
