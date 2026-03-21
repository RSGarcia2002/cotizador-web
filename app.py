from flask import Flask, render_template, request, make_response, redirect
from datetime import datetime, timedelta
from weasyprint import HTML
from urllib.parse import urlencode
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def obtener_conexion():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise ValueError("No se encontró DATABASE_URL en las variables de entorno.")

    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def init_db():
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cotizaciones (
        id SERIAL PRIMARY KEY,
        no_referencia TEXT NOT NULL,
        fecha TEXT NOT NULL,
        empresa TEXT NOT NULL,
        ingeniero TEXT,
        asunto TEXT NOT NULL,
        total_numero DOUBLE PRECISION NOT NULL,
        total_letras TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Pendiente',
        pdf_nombre TEXT,
        su_referencia TEXT,
        precio_texto TEXT,
        tiempo_entrega TEXT,
        validez TEXT,
        encargado TEXT,
        contacto_nombre TEXT,
        contacto_telefono TEXT,
        contacto_correo TEXT,
        filas_html TEXT,
        items_json TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS empresas (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingenieros (
        id SERIAL PRIMARY KEY,
        empresa_id INTEGER NOT NULL,
        titulo TEXT,
        nombre TEXT NOT NULL,
        FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS asuntos_frecuentes (
        id SERIAL PRIMARY KEY,
        empresa_id INTEGER,
        asunto TEXT NOT NULL,
        FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        clave TEXT PRIMARY KEY,
        valor TEXT NOT NULL
    )
    """)

    cur.execute("""
    INSERT INTO configuracion (clave, valor)
    VALUES (%s, %s)
    ON CONFLICT (clave) DO NOTHING
    """, ("correlativo", "1"))

    conn.commit()
    cur.close()
    conn.close()


def seed_db():
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO empresas (nombre)
        VALUES (%s)
        ON CONFLICT (nombre) DO NOTHING
    """, ("GLAD",))

    cur.execute("""
        INSERT INTO empresas (nombre)
        VALUES (%s)
        ON CONFLICT (nombre) DO NOTHING
    """, ("Chocolates",))

    cur.execute("SELECT id, nombre FROM empresas")
    empresas = {row["nombre"]: row["id"] for row in cur.fetchall()}

    if "GLAD" in empresas:
        cur.execute("""
            INSERT INTO ingenieros (empresa_id, titulo, nombre)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM ingenieros WHERE empresa_id = %s AND nombre = %s
            )
        """, (empresas["GLAD"], "Ing.", "Néstor", empresas["GLAD"], "Néstor"))

    if "Chocolates" in empresas:
        cur.execute("""
            INSERT INTO ingenieros (empresa_id, titulo, nombre)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM ingenieros WHERE empresa_id = %s AND nombre = %s
            )
        """, (empresas["Chocolates"], "Lic.", "William", empresas["Chocolates"], "William"))

    cur.execute("""
        INSERT INTO asuntos_frecuentes (empresa_id, asunto)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM asuntos_frecuentes WHERE empresa_id = %s AND asunto = %s
        )
    """, (
        empresas.get("GLAD"),
        "TRABAJOS MANTENIMIENTO TABLEROS ELÉCTRICOS PLANTA GLAD",
        empresas.get("GLAD"),
        "TRABAJOS MANTENIMIENTO TABLEROS ELÉCTRICOS PLANTA GLAD"
    ))

    cur.execute("""
        INSERT INTO asuntos_frecuentes (empresa_id, asunto)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM asuntos_frecuentes WHERE empresa_id = %s AND asunto = %s
        )
    """, (
        empresas.get("GLAD"),
        "APOYO DE PERSONAL PARA CONSTRUCCIÓN DE ACOMETIDA ELÉCTRICA",
        empresas.get("GLAD"),
        "APOYO DE PERSONAL PARA CONSTRUCCIÓN DE ACOMETIDA ELÉCTRICA"
    ))

    conn.commit()
    cur.close()
    conn.close()


def obtener_fecha_guatemala():
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    hoy = datetime.now()
    return f"Guatemala, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"


def obtener_fecha_validez():
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    fecha_validez = datetime.now() + timedelta(days=30)
    return f"{fecha_validez.day} de {meses[fecha_validez.month - 1]} de {fecha_validez.year}"


def obtener_no_referencia():
    anio = datetime.now().year

    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT valor FROM configuracion WHERE clave = %s", ("correlativo",))
    row = cur.fetchone()
    cur.close()
    conn.close()

    correlativo = int(row["valor"]) if row else 1
    return f"NT-{anio}-{correlativo:04d}"


def incrementar_correlativo():
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("SELECT valor FROM configuracion WHERE clave = %s", ("correlativo",))
    row = cur.fetchone()

    correlativo = int(row["valor"]) if row else 1
    correlativo += 1

    cur.execute("""
        INSERT INTO configuracion (clave, valor)
        VALUES (%s, %s)
        ON CONFLICT (clave)
        DO UPDATE SET valor = EXCLUDED.valor
    """, ("correlativo", str(correlativo)))

    conn.commit()
    cur.close()
    conn.close()


def obtener_empresas():
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM empresas ORDER BY nombre")
    empresas = cur.fetchall()
    cur.close()
    conn.close()
    return empresas


def obtener_ingenieros_por_empresa(empresa_id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre, titulo
        FROM ingenieros
        WHERE empresa_id = %s
        ORDER BY nombre
    """, (empresa_id,))
    ingenieros = cur.fetchall()
    cur.close()
    conn.close()
    return ingenieros


def obtener_asuntos_sugeridos(empresa_id=None):
    conn = obtener_conexion()
    cur = conn.cursor()

    if empresa_id:
        cur.execute("""
            SELECT asunto
            FROM asuntos_frecuentes
            WHERE empresa_id = %s OR empresa_id IS NULL
            ORDER BY asunto
        """, (empresa_id,))
    else:
        cur.execute("""
            SELECT asunto
            FROM asuntos_frecuentes
            ORDER BY asunto
        """)

    asuntos = cur.fetchall()
    cur.close()
    conn.close()
    return asuntos


@app.route("/")
def index():
    fecha = obtener_fecha_guatemala()
    validez = obtener_fecha_validez()
    no_referencia = obtener_no_referencia()

    datos_fijos = {
        "precio_texto": "Se entienden netos en Quetzales",
        "tiempo_entrega": "Inmediata",
        "encargado": "Melvin Siney",
        "contacto_nombre": "Melvin Siney",
        "contacto_telefono": "5502-5762",
        "contacto_correo": "melvinsiney@gmail.com"
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
        "fecha": request.args.get("fecha", fecha)
    }

    return render_template(
        "index.html",
        fecha=duplicado["fecha"],
        validez=duplicado["validez"],
        no_referencia=duplicado["no_referencia"],
        datos_fijos=datos_fijos,
        duplicado=duplicado,
        empresas=obtener_empresas()
    )


@app.route("/exportar-pdf", methods=["POST"])
def exportar_pdf():
    data = request.form.to_dict()

    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cotizaciones (
            no_referencia, fecha, empresa, ingeniero, asunto,
            total_numero, total_letras, estado, pdf_nombre,
            su_referencia, precio_texto, tiempo_entrega, validez,
            encargado, contacto_nombre, contacto_telefono,
            contacto_correo, filas_html, items_json
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
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
        data.get("items_json", "")
    ))

    conn.commit()
    cur.close()
    conn.close()

    html = render_template("pdf_template.html", data=data)
    pdf = HTML(string=html).write_pdf()

    incrementar_correlativo()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={data.get('no_referencia', 'cotizacion')}.pdf"
    return response


@app.route("/cotizaciones")
def cotizaciones():
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, no_referencia, fecha, empresa, ingeniero, asunto,
               total_numero, estado, filas_html, items_json
        FROM cotizaciones
        ORDER BY id DESC
    """)
    cotizaciones = cur.fetchall()

    cur.execute("""
        SELECT COALESCE(SUM(total_numero), 0) AS total
        FROM cotizaciones
        WHERE estado = %s
    """, ("Aprobada",))
    total_mes = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return render_template(
        "cotizaciones.html",
        cotizaciones=cotizaciones,
        total_mes=total_mes
    )


@app.route("/cambiar-estado/<int:id>", methods=["POST"])
def cambiar_estado(id):
    nuevo_estado = request.form.get("estado", "Pendiente")

    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("UPDATE cotizaciones SET estado = %s WHERE id = %s", (nuevo_estado, id))
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/cotizaciones")


@app.route("/descargar-pdf/<int:id>")
def descargar_pdf_historial(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cotizaciones WHERE id = %s", (id,))
    cotizacion = cur.fetchone()
    cur.close()
    conn.close()

    if not cotizacion:
        return "Cotización no encontrada", 404

    fecha_texto = cotizacion["fecha"]
    fecha_corta = ""

    try:
        partes = fecha_texto.replace("Guatemala,", "").strip().split(" de ")
        if len(partes) == 3:
            mes = partes[1]
            anio = partes[2]
            fecha_corta = f"{mes} de {anio}"
    except Exception:
        fecha_corta = ""

    data = {
        "fecha": cotizacion["fecha"],
        "fecha_corta": fecha_corta,
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
        "contacto_correo": cotizacion["contacto_correo"]
    }

    html = render_template("pdf_template.html", data=data)
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={cotizacion['no_referencia']}.pdf"
    return response


@app.route("/duplicar/<int:id>")
def duplicar_cotizacion(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cotizaciones WHERE id = %s", (id,))
    c = cur.fetchone()
    cur.close()
    conn.close()

    if not c:
        return "Cotización no encontrada", 404

    params = urlencode({
        "empresa": c["empresa"] or "",
        "ingeniero": c["ingeniero"] or "",
        "su_referencia": c["su_referencia"] or "",
        "asunto": c["asunto"] or "",
        "encargado": c["encargado"] or "",
        "contacto_nombre": c["contacto_nombre"] or "",
        "contacto_telefono": c["contacto_telefono"] or "",
        "contacto_correo": c["contacto_correo"] or "",
        "items_json": c["items_json"] or "[]"
    })

    return redirect(f"/?{params}")


@app.route("/editar/<int:id>")
def editar_cotizacion(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cotizaciones WHERE id = %s", (id,))
    c = cur.fetchone()
    cur.close()
    conn.close()

    if not c:
        return "Cotización no encontrada", 404

    params = urlencode({
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
        "fecha": c["fecha"] or ""
    })

    return redirect(f"/?{params}")


@app.route("/guardar-edicion", methods=["POST"])
def guardar_edicion():
    data = request.form.to_dict()
    cotizacion_id = data.get("cotizacion_id")

    if not cotizacion_id:
        return "ID de cotización no recibido", 400

    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
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
    """, (
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
        cotizacion_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/cotizaciones")


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_cotizacion(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM cotizaciones WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/cotizaciones")


@app.route("/api/ingenieros/<int:empresa_id>")
def api_ingenieros(empresa_id):
    ingenieros = obtener_ingenieros_por_empresa(empresa_id)
    return {
        "ingenieros": [
            {
                "id": i["id"],
                "nombre": i["nombre"],
                "titulo": i["titulo"] or "",
                "nombre_mostrar": f"{(i['titulo'] or '').strip()} {(i['nombre'] or '').strip()}".strip()
            }
            for i in ingenieros
        ]
    }


@app.route("/catalogos")
def catalogos():
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nombre
        FROM empresas
        ORDER BY nombre
    """)
    empresas = cur.fetchall()

    cur.execute("""
        SELECT ingenieros.id, ingenieros.titulo, ingenieros.nombre, empresas.nombre AS empresa_nombre
        FROM ingenieros
        INNER JOIN empresas ON ingenieros.empresa_id = empresas.id
        ORDER BY empresas.nombre, ingenieros.nombre
    """)
    ingenieros = cur.fetchall()

    cur.execute("""
        SELECT asuntos_frecuentes.id,
               asuntos_frecuentes.asunto,
               empresas.nombre AS empresa_nombre
        FROM asuntos_frecuentes
        LEFT JOIN empresas ON asuntos_frecuentes.empresa_id = empresas.id
        ORDER BY empresas.nombre, asuntos_frecuentes.asunto
    """)
    asuntos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("catalogos.html", empresas=empresas, ingenieros=ingenieros, asuntos=asuntos)


@app.route("/agregar-empresa", methods=["POST"])
def agregar_empresa():
    nombre = request.form.get("nombre", "").strip()

    if nombre:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO empresas (nombre)
            VALUES (%s)
            ON CONFLICT (nombre) DO NOTHING
        """, (nombre,))
        conn.commit()
        cur.close()
        conn.close()

    return redirect("/catalogos")


@app.route("/agregar-ingeniero", methods=["POST"])
def agregar_ingeniero():
    empresa_id = request.form.get("empresa_id", "").strip()
    titulo = request.form.get("titulo", "").strip()
    nombre = request.form.get("nombre", "").strip()

    if empresa_id and nombre:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ingenieros (empresa_id, titulo, nombre)
            VALUES (%s, %s, %s)
        """, (empresa_id, titulo, nombre))
        conn.commit()
        cur.close()
        conn.close()

    return redirect("/catalogos")


@app.route("/api/asuntos")
def api_asuntos():
    empresa_id = request.args.get("empresa_id", type=int)
    asuntos = obtener_asuntos_sugeridos(empresa_id)

    return {
        "asuntos": [a["asunto"] for a in asuntos]
    }


@app.route("/agregar-asunto", methods=["POST"])
def agregar_asunto():
    empresa_id = request.form.get("empresa_id", "").strip()
    asunto = request.form.get("asunto", "").strip()

    empresa_id_valor = None if empresa_id == "" else int(empresa_id)

    if asunto:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO asuntos_frecuentes (empresa_id, asunto)
            VALUES (%s, %s)
        """, (empresa_id_valor, asunto))
        conn.commit()
        cur.close()
        conn.close()

    return redirect("/catalogos")


@app.route("/eliminar-empresa/<int:id>", methods=["POST"])
def eliminar_empresa(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM ingenieros WHERE empresa_id = %s", (id,))
    cur.execute("DELETE FROM asuntos_frecuentes WHERE empresa_id = %s", (id,))
    cur.execute("DELETE FROM empresas WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/catalogos")


@app.route("/eliminar-ingeniero/<int:id>", methods=["POST"])
def eliminar_ingeniero(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM ingenieros WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/catalogos")


@app.route("/eliminar-asunto/<int:id>", methods=["POST"])
def eliminar_asunto(id):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM asuntos_frecuentes WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/catalogos")


if __name__ == "__main__":
    init_db()
    seed_db()
    app.run(debug=True)