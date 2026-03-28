from db import execute, fetch_all


def init_db():
    execute(
        """
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
        """
    )

    execute(
        """
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
        """
    )

    execute(
        """
        CREATE TABLE IF NOT EXISTS ingenieros (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER NOT NULL,
            titulo TEXT,
            nombre TEXT NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )
        """
    )

    execute(
        """
        CREATE TABLE IF NOT EXISTS asuntos_frecuentes (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER,
            asunto TEXT NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )
        """
    )

    execute(
        """
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
        """
    )

    execute(
        """
        INSERT INTO configuracion (clave, valor)
        VALUES (%s, %s)
        ON CONFLICT (clave) DO NOTHING
        """,
        ("correlativo", "1"),
    )
<<<<<<< HEAD
    execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
=======
>>>>>>> fe5b4f2c2390e361d3a9a9d15caaf0af4a550ce8

    # =========================
    # AMPLIAR TABLA EMPRESAS
    # =========================
    execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS nit TEXT")
    execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS direccion TEXT")
    execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS dias_credito INTEGER NOT NULL DEFAULT 30")
    execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS plantilla_ocr TEXT")
    execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS formato_descripcion_sat TEXT")
    execute("ALTER TABLE empresas ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE")

    # =========================
    # ORDENES DE COMPRA
    # =========================
    execute(
        """
        CREATE TABLE IF NOT EXISTS ordenes_compra (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER NOT NULL,
            numero_orden TEXT NOT NULL,
            fecha_orden DATE,
            subtotal DOUBLE PRECISION NOT NULL DEFAULT 0,
            iva DOUBLE PRECISION NOT NULL DEFAULT 0,
            total DOUBLE PRECISION NOT NULL DEFAULT 0,
            moneda TEXT NOT NULL DEFAULT 'GTQ',
            proyecto TEXT,
            descripcion_extraida TEXT,
            condiciones_pago TEXT,
            dias_credito INTEGER,
            fecha_estimada_pago DATE,
            estado TEXT NOT NULL DEFAULT 'Pendiente de facturar',
            archivo_orden TEXT,
            datos_ocr_json TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE RESTRICT
        )
        """
    )

    execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_ordenes_compra_empresa_numero
        ON ordenes_compra (empresa_id, numero_orden)
        """
    )

    # =========================
    # FACTURAS DE ORDENES
    # =========================
    execute(
        """
        CREATE TABLE IF NOT EXISTS facturas_oc (
            id SERIAL PRIMARY KEY,
            orden_compra_id INTEGER NOT NULL UNIQUE,
            numero_factura TEXT,
            fecha_factura DATE,
            nit_facturado TEXT,
            direccion_facturada TEXT,
            descripcion_sat TEXT,
            monto_facturado DOUBLE PRECISION NOT NULL DEFAULT 0,
            archivo_factura TEXT,
            archivo_expediente TEXT,
            fecha_pago_real DATE,
            estado_pago TEXT NOT NULL DEFAULT 'Pendiente',
            observaciones TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            FOREIGN KEY (orden_compra_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE
        )
        """
    )


def seed_db():
    execute(
        """
        INSERT INTO empresas (
            nombre, nit, direccion, dias_credito, plantilla_ocr, formato_descripcion_sat
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (nombre) DO NOTHING
        """,
        (
            "GLAD",
            "4399620-5",
            "",
            30,
            "glad_naturalisimo",
            "Trabajos realizados según orden de compra No. {numero_orden} por proyecto {proyecto}.",
        ),
    )

    execute(
        """
        INSERT INTO empresas (
            nombre, nit, direccion, dias_credito, plantilla_ocr, formato_descripcion_sat
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (nombre) DO NOTHING
        """,
        (
            "Chocolates",
            "",
            "",
            30,
            "chocolates_best",
            "Trabajos realizados según orden de compra No. {numero_orden} por proyecto {proyecto}.",
        ),
    )

    empresas = {row["nombre"]: row["id"] for row in fetch_all("SELECT id, nombre FROM empresas")}

    if "GLAD" in empresas:
        execute(
            """
            INSERT INTO ingenieros (empresa_id, titulo, nombre)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM ingenieros WHERE empresa_id = %s AND nombre = %s
            )
            """,
            (empresas["GLAD"], "Ing.", "Néstor", empresas["GLAD"], "Néstor"),
        )

    if "Chocolates" in empresas:
        execute(
            """
            INSERT INTO ingenieros (empresa_id, titulo, nombre)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM ingenieros WHERE empresa_id = %s AND nombre = %s
            )
            """,
            (empresas["Chocolates"], "Lic.", "William", empresas["Chocolates"], "William"),
        )

    execute(
        """
        INSERT INTO asuntos_frecuentes (empresa_id, asunto)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM asuntos_frecuentes WHERE empresa_id = %s AND asunto = %s
        )
        """,
        (
            empresas.get("GLAD"),
            "TRABAJOS MANTENIMIENTO TABLEROS ELÉCTRICOS PLANTA GLAD",
            empresas.get("GLAD"),
            "TRABAJOS MANTENIMIENTO TABLEROS ELÉCTRICOS PLANTA GLAD",
        ),
    )

    execute(
        """
        INSERT INTO asuntos_frecuentes (empresa_id, asunto)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM asuntos_frecuentes WHERE empresa_id = %s AND asunto = %s
        )
        """,
        (
            empresas.get("GLAD"),
            "APOYO DE PERSONAL PARA CONSTRUCCIÓN DE ACOMETIDA ELÉCTRICA",
            empresas.get("GLAD"),
            "APOYO DE PERSONAL PARA CONSTRUCCIÓN DE ACOMETIDA ELÉCTRICA",
        ),
    )