from datetime import date
from db import fetch_all, fetch_one, execute
import json
import os
from pypdf import PdfReader, PdfWriter

def obtener_ordenes():
    query = """
        SELECT
            oc.id,
            e.nombre AS empresa,
            oc.numero_orden,
            oc.fecha_orden,
            oc.total,
            oc.estado,
            oc.fecha_estimada_pago,
            foc.estado_pago,
            foc.fecha_factura,
            foc.fecha_pago_real
        FROM ordenes_compra oc
        JOIN empresas e ON e.id = oc.empresa_id
        LEFT JOIN facturas_oc foc ON foc.orden_compra_id = oc.id
        ORDER BY oc.created_at DESC, oc.id DESC
    """
    ordenes = fetch_all(query)

    for orden in ordenes:
        orden["semaforo"] = calcular_semaforo(orden)

    return ordenes


def calcular_semaforo(orden):
    estado_pago = orden.get("estado_pago")
    estado = orden.get("estado")
    fecha_estimada = orden.get("fecha_estimada_pago")
    fecha_pago_real = orden.get("fecha_pago_real")

    if estado_pago == "Pagada":
        return "Pagada"

    if estado == "Pendiente de facturar":
        return "Pendiente de facturar"

    if not fecha_estimada:
        return "Sin fecha estimada"

    hoy = date.today()
    delta = (fecha_estimada - hoy).days

    if fecha_pago_real:
        atraso = (fecha_pago_real - fecha_estimada).days
        if atraso > 0:
            return f"Pagada con {atraso} día(s) de atraso"
        elif atraso < 0:
            return f"Pagada {-atraso} día(s) antes"
        return "Pagada el día exacto"

    if delta > 0:
        return f"Faltan {delta} día(s)"
    elif delta == 0:
        return "Vence hoy"
    else:
        return f"Lleva {abs(delta)} día(s) de atraso"


def obtener_empresas_activas():
    return fetch_all(
        """
        SELECT id, nombre, nit, direccion, dias_credito
        FROM empresas
        WHERE activo = TRUE
        ORDER BY nombre ASC
        """
    )


def obtener_empresa_por_id(empresa_id):
    return fetch_one(
        """
        SELECT id, nombre, nit, direccion, dias_credito, plantilla_ocr, formato_descripcion_sat
        FROM empresas
        WHERE id = %s
        """,
        (empresa_id,),
    )


def crear_orden_compra(data):
    empresa = obtener_empresa_por_id(data["empresa_id"])
    dias_credito = data.get("dias_credito") or (empresa["dias_credito"] if empresa else 30)

    fecha_estimada_pago = None
    if data.get("fecha_orden") and dias_credito is not None:
        fecha_estimada_pago_query = """
            SELECT (%s::date + (%s || ' days')::interval)::date AS fecha_estimada_pago
        """
        row = fetch_one(fecha_estimada_pago_query, (data["fecha_orden"], int(dias_credito)))
        if row:
            fecha_estimada_pago = row["fecha_estimada_pago"]

    execute(
        """
        INSERT INTO ordenes_compra (
            empresa_id,
            numero_orden,
            fecha_orden,
            subtotal,
            iva,
            total,
            moneda,
            proyecto,
            descripcion_extraida,
            condiciones_pago,
            dias_credito,
            fecha_estimada_pago,
            estado,
            archivo_orden,
            datos_ocr_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["empresa_id"],
            data["numero_orden"],
            data.get("fecha_orden") or None,
            float(data.get("subtotal") or 0),
            float(data.get("iva") or 0),
            float(data.get("total") or 0),
            data.get("moneda") or "GTQ",
            data.get("proyecto") or "",
            data.get("descripcion_extraida") or "",
            data.get("condiciones_pago") or "",
            dias_credito,
            fecha_estimada_pago,
            "Pendiente de facturar",
            data.get("archivo_orden") or "",
            data.get("datos_ocr_json") or "",
        ),
    )
    
def obtener_orden_por_id(orden_id):
    query = """
        SELECT
            oc.id,
            oc.empresa_id,
            e.nombre AS empresa,
            e.nit AS empresa_nit,
            e.direccion AS empresa_direccion,
            e.dias_credito AS empresa_dias_credito,
            e.formato_descripcion_sat,
            e.plantilla_ocr,
            oc.numero_orden,
            oc.fecha_orden,
            oc.subtotal,
            oc.iva,
            oc.total,
            oc.moneda,
            oc.proyecto,
            oc.descripcion_extraida,
            oc.condiciones_pago,
            oc.dias_credito,
            oc.fecha_estimada_pago,
            oc.estado,
            oc.archivo_orden,
            oc.datos_ocr_json,
            foc.id AS factura_id,
            foc.numero_factura,
            foc.fecha_factura,
            foc.nit_facturado,
            foc.direccion_facturada,
            foc.descripcion_sat,
            foc.monto_facturado,
            foc.archivo_factura,
            foc.archivo_expediente,
            foc.fecha_pago_real,
            foc.estado_pago,
            foc.observaciones
        FROM ordenes_compra oc
        JOIN empresas e ON e.id = oc.empresa_id
        LEFT JOIN facturas_oc foc ON foc.orden_compra_id = oc.id
        WHERE oc.id = %s
    """
    orden = fetch_one(query, (orden_id,))
    if orden:
        orden["semaforo"] = calcular_semaforo(orden)
        orden["descripcion_sat_sugerida"] = generar_descripcion_sat(orden)
    return orden


def generar_descripcion_sat(orden):
    plantilla = orden.get("formato_descripcion_sat") or \
        "Trabajos realizados según orden de compra No. {numero_orden} por proyecto {proyecto}."

    return plantilla.format(
        numero_orden=orden.get("numero_orden", "") or "",
        proyecto=orden.get("proyecto", "") or orden.get("descripcion_extraida", "") or ""
    )    
    
def registrar_factura_orden(orden_id, data):
    execute(
        """
        INSERT INTO facturas_oc (
            orden_compra_id,
            numero_factura,
            fecha_factura,
            nit_facturado,
            direccion_facturada,
            descripcion_sat,
            monto_facturado,
            archivo_factura,
            archivo_expediente,
            estado_pago,
            observaciones
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (orden_compra_id)
        DO UPDATE SET
            numero_factura = EXCLUDED.numero_factura,
            fecha_factura = EXCLUDED.fecha_factura,
            nit_facturado = EXCLUDED.nit_facturado,
            direccion_facturada = EXCLUDED.direccion_facturada,
            descripcion_sat = EXCLUDED.descripcion_sat,
            monto_facturado = EXCLUDED.monto_facturado,
            archivo_factura = EXCLUDED.archivo_factura,
            archivo_expediente = EXCLUDED.archivo_expediente,
            estado_pago = EXCLUDED.estado_pago,
            observaciones = EXCLUDED.observaciones,
            updated_at = NOW()
        """,
        (
            orden_id,
            data.get("numero_factura") or "",
            data.get("fecha_factura") or None,
            data.get("nit_facturado") or "",
            data.get("direccion_facturada") or "",
            data.get("descripcion_sat") or "",
            float(data.get("monto_facturado") or 0),
            data.get("archivo_factura") or "",
            data.get("archivo_expediente") or "",
            "Pendiente",
            data.get("observaciones") or "",
        ),
    )

    execute(
        """
        UPDATE ordenes_compra
        SET estado = 'Facturada',
            updated_at = NOW()
        WHERE id = %s
        """,
        (orden_id,),
    )
    
def marcar_factura_pagada(orden_id, fecha_pago_real, observaciones=""):
    execute(
        """
        UPDATE facturas_oc
        SET estado_pago = 'Pagada',
            fecha_pago_real = %s,
            observaciones = COALESCE(NULLIF(%s, ''), observaciones),
            updated_at = NOW()
        WHERE orden_compra_id = %s
        """,
        (fecha_pago_real, observaciones, orden_id),
    )
    
def guardar_resultado_extraccion_orden(orden_id, texto_extraido, metodo):
    payload = json.dumps({
        "metodo": metodo,
        "texto": texto_extraido,
    }, ensure_ascii=False)

    execute(
        """
        UPDATE ordenes_compra
        SET
            descripcion_extraida = %s,
            datos_ocr_json = %s,
            updated_at = NOW()
        WHERE id = %s
        """,
        (texto_extraido, payload, orden_id),
    )    
def aplicar_datos_parseados_a_orden(orden_id, datos):
    execute(
        """
        UPDATE ordenes_compra
        SET
            numero_orden = COALESCE(%s, numero_orden),
            fecha_orden = COALESCE(%s, fecha_orden),
            subtotal = COALESCE(%s, subtotal),
            iva = COALESCE(%s, iva),
            total = COALESCE(%s, total),
            proyecto = COALESCE(%s, proyecto),
            condiciones_pago = COALESCE(%s, condiciones_pago),
            updated_at = NOW()
        WHERE id = %s
        """,
        (
            datos.get("numero_orden"),
            datos.get("fecha_orden"),
            datos.get("subtotal"),
            datos.get("iva"),
            datos.get("total"),
            datos.get("proyecto"),
            datos.get("condiciones_pago"),
            orden_id,
        ),
    )    
    
def generar_expediente_unificado(
    orden_pdf_path: str,
    factura_pdf_path: str,
    salida_pdf_path: str,
):
    writer = PdfWriter()

    for path in [orden_pdf_path, factura_pdf_path]:
        if path and os.path.exists(path):
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)

    with open(salida_pdf_path, "wb") as f:
        writer.write(f)    