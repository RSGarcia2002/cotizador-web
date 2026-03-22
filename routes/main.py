from flask import Blueprint, make_response, redirect, render_template, request ,jsonify
from weasyprint import HTML
from openpyxl import load_workbook
import io

from services.catalog_service import (
    agregar_asunto,
    agregar_empresa,
    agregar_ingeniero,
    eliminar_asunto,
    eliminar_empresa,
    eliminar_ingeniero,
    listar_catalogos,
    obtener_asuntos_sugeridos,
    obtener_empresas,
    obtener_ingenieros_por_empresa,
)
from services.cotizacion_service import (
    actualizar_cotizacion,
    actualizar_estado,
    construir_params_duplicado,
    construir_params_edicion,
    crear_cotizacion,
    eliminar_cotizacion,
    incrementar_correlativo,
    listar_cotizaciones,
    obtener_cotizacion,
    obtener_no_referencia,
    preparar_data_pdf,
)
from services.helpers import fecha_guatemala, fecha_validez

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    fecha = fecha_guatemala()
    validez = fecha_validez()
    no_referencia = obtener_no_referencia()

    datos_fijos = {
        "precio_texto": "Se entienden netos en Quetzales",
        "tiempo_entrega": "Inmediata",
        "encargado": "Melvin Siney",
        "contacto_nombre": "Melvin Siney",
        "contacto_telefono": "5502-5762",
        "contacto_correo": "melvinsiney@gmail.com",
    }

    duplicado = {
        "id": request.args.get("id", ""),
        "modo_edicion": request.args.get("modo_edicion", "0"),
        "empresa": request.args.get("empresa", ""),
        "ingeniero": request.args.get("ingeniero", ""),
        "su_referencia": request.args.get("su_referencia", ""),
        "asunto": request.args.get("asunto", ""),
        "encargado": request.args.get("encargado", datos_fijos["encargado"]),
        "contacto_nombre": request.args.get("contacto_nombre", datos_fijos["contacto_nombre"]),
        "contacto_telefono": request.args.get("contacto_telefono", datos_fijos["contacto_telefono"]),
        "contacto_correo": request.args.get("contacto_correo", datos_fijos["contacto_correo"]),
        "items_json": request.args.get("items_json", "[]"),
        "precio_texto": request.args.get("precio_texto", datos_fijos["precio_texto"]),
        "tiempo_entrega": request.args.get("tiempo_entrega", datos_fijos["tiempo_entrega"]),
        "validez": request.args.get("validez", validez),
        "no_referencia": request.args.get("no_referencia", no_referencia),
        "fecha": request.args.get("fecha", fecha),
    }

    return render_template(
        "index.html",
        fecha=duplicado["fecha"],
        validez=duplicado["validez"],
        no_referencia=duplicado["no_referencia"],
        datos_fijos=datos_fijos,
        duplicado=duplicado,
        empresas=obtener_empresas(),
    )


@bp.route("/exportar-pdf", methods=["POST"])
def exportar_pdf():
    data = request.form.to_dict()
    crear_cotizacion(data)
    html = render_template("pdf_template.html", data=data)
    pdf = HTML(string=html).write_pdf()
    incrementar_correlativo()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={data.get('no_referencia', 'cotizacion')}.pdf"
    return response


@bp.route("/cotizaciones")
def cotizaciones():
    cotizaciones_data, total_mes = listar_cotizaciones()
    return render_template("cotizaciones.html", cotizaciones=cotizaciones_data, total_mes=total_mes)


@bp.route("/cambiar-estado/<int:id>", methods=["POST"])
def cambiar_estado(id):
    actualizar_estado(id, request.form.get("estado", "Pendiente"))
    return redirect("/cotizaciones")


@bp.route("/descargar-pdf/<int:id>")
def descargar_pdf_historial(id):
    cotizacion = obtener_cotizacion(id)
    if not cotizacion:
        return "Cotización no encontrada", 404

    html = render_template("pdf_template.html", data=preparar_data_pdf(cotizacion))
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={cotizacion['no_referencia']}.pdf"
    return response


@bp.route("/duplicar/<int:id>")
def duplicar_cotizacion(id):
    cotizacion = obtener_cotizacion(id)
    if not cotizacion:
        return "Cotización no encontrada", 404
    return redirect(f"/?{construir_params_duplicado(cotizacion)}")


@bp.route("/editar/<int:id>")
def editar_cotizacion(id):
    cotizacion = obtener_cotizacion(id)
    if not cotizacion:
        return "Cotización no encontrada", 404
    return redirect(f"/?{construir_params_edicion(cotizacion)}")


@bp.route("/guardar-edicion", methods=["POST"])
def guardar_edicion():
    data = request.form.to_dict()
    if not data.get("cotizacion_id"):
        return "ID de cotización no recibido", 400
    actualizar_cotizacion(data)
    return redirect("/cotizaciones")


@bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    eliminar_cotizacion(id)
    return redirect("/cotizaciones")


@bp.route("/api/ingenieros/<int:empresa_id>")
def api_ingenieros(empresa_id):
    ingenieros = obtener_ingenieros_por_empresa(empresa_id)
    return {
        "ingenieros": [
            {
                "id": i["id"],
                "nombre": i["nombre"],
                "titulo": i["titulo"] or "",
                "nombre_mostrar": f"{(i['titulo'] or '').strip()} {(i['nombre'] or '').strip()}".strip(),
            }
            for i in ingenieros
        ]
    }


@bp.route("/api/asuntos")
def api_asuntos():
    empresa_id = request.args.get("empresa_id", type=int)
    asuntos = obtener_asuntos_sugeridos(empresa_id)
    return {"asuntos": [a["asunto"] for a in asuntos]}


@bp.route("/catalogos")
def catalogos():
    empresas, ingenieros, asuntos = listar_catalogos()
    return render_template("catalogos.html", empresas=empresas, ingenieros=ingenieros, asuntos=asuntos)


@bp.route("/agregar-empresa", methods=["POST"])
def crear_empresa():
    nombre = request.form.get("nombre", "").strip()
    if nombre:
        agregar_empresa(nombre)
    return redirect("/catalogos")


@bp.route("/agregar-ingeniero", methods=["POST"])
def crear_ingeniero():
    empresa_id = request.form.get("empresa_id", "").strip()
    titulo = request.form.get("titulo", "").strip()
    nombre = request.form.get("nombre", "").strip()
    if empresa_id and nombre:
        agregar_ingeniero(int(empresa_id), titulo, nombre)
    return redirect("/catalogos")


@bp.route("/agregar-asunto", methods=["POST"])
def crear_asunto():
    empresa_id = request.form.get("empresa_id", "").strip()
    asunto = request.form.get("asunto", "").strip()
    if asunto:
        agregar_asunto(None if empresa_id == "" else int(empresa_id), asunto)
    return redirect("/catalogos")


@bp.route("/eliminar-empresa/<int:id>", methods=["POST"])
def borrar_empresa(id):
    eliminar_empresa(id)
    return redirect("/catalogos")


@bp.route("/eliminar-ingeniero/<int:id>", methods=["POST"])
def borrar_ingeniero(id):
    eliminar_ingeniero(id)
    return redirect("/catalogos")


@bp.route("/eliminar-asunto/<int:id>", methods=["POST"])
def borrar_asunto(id):
    eliminar_asunto(id)
    return redirect("/catalogos")

@bp.route("/importar-excel", methods=["POST"])
def importar_excel():
    archivo = request.files.get("archivo")

    if not archivo:
        return jsonify({"ok": False, "error": "No se envió ningún archivo."}), 400

    try:
        contenido = io.BytesIO(archivo.read())
        wb = load_workbook(contenido, data_only=True)
        ws = wb.active

        filas = list(ws.iter_rows(values_only=True))
        if not filas or len(filas) < 2:
            return jsonify({"ok": False, "error": "El archivo está vacío o no tiene datos."}), 400

        encabezados = [str(c).strip().lower() if c is not None else "" for c in filas[0]]

        try:
            idx_cantidad = encabezados.index("cantidad")
            idx_descripcion = encabezados.index("descripcion")
            idx_precio = encabezados.index("precio_unitario")
        except ValueError:
            return jsonify({
                "ok": False,
                "error": "El Excel debe tener las columnas: cantidad, descripcion, precio_unitario"
            }), 400

        items = []
        for fila in filas[1:]:
            if not fila:
                continue

            cantidad = fila[idx_cantidad] if idx_cantidad < len(fila) else None
            descripcion = fila[idx_descripcion] if idx_descripcion < len(fila) else None
            precio = fila[idx_precio] if idx_precio < len(fila) else None

            if descripcion in (None, ""):
                continue

            try:
                cantidad = float(cantidad or 0)
            except Exception:
                cantidad = 0

            try:
                precio = float(precio or 0)
            except Exception:
                precio = 0

            items.append({
                "cantidad": cantidad,
                "descripcion": str(descripcion).strip(),
                "precio_unitario": precio
            })

        return jsonify({"ok": True, "items": items})

    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al leer el Excel: {str(e)}"}), 500