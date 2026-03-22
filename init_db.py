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



def seed_db():
    execute(
        "INSERT INTO empresas (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
        ("GLAD",),
    )
    execute(
        "INSERT INTO empresas (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
        ("Chocolates",),
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
