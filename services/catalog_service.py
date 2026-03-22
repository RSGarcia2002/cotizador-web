from db import fetch_all, execute


def obtener_empresas():
    return fetch_all("SELECT id, nombre FROM empresas ORDER BY nombre")



def obtener_ingenieros_por_empresa(empresa_id: int):
    return fetch_all(
        """
        SELECT id, nombre, titulo
        FROM ingenieros
        WHERE empresa_id = %s
        ORDER BY nombre
        """,
        (empresa_id,),
    )



def obtener_asuntos_sugeridos(empresa_id=None):
    if empresa_id:
        return fetch_all(
            """
            SELECT asunto
            FROM asuntos_frecuentes
            WHERE empresa_id = %s OR empresa_id IS NULL
            ORDER BY asunto
            """,
            (empresa_id,),
        )
    return fetch_all(
        """
        SELECT asunto
        FROM asuntos_frecuentes
        ORDER BY asunto
        """
    )



def listar_catalogos():
    empresas = fetch_all("SELECT id, nombre FROM empresas ORDER BY nombre")
    ingenieros = fetch_all(
        """
        SELECT ingenieros.id, ingenieros.titulo, ingenieros.nombre, empresas.nombre AS empresa_nombre
        FROM ingenieros
        INNER JOIN empresas ON ingenieros.empresa_id = empresas.id
        ORDER BY empresas.nombre, ingenieros.nombre
        """
    )
    asuntos = fetch_all(
        """
        SELECT asuntos_frecuentes.id,
               asuntos_frecuentes.asunto,
               empresas.nombre AS empresa_nombre
        FROM asuntos_frecuentes
        LEFT JOIN empresas ON asuntos_frecuentes.empresa_id = empresas.id
        ORDER BY empresas.nombre, asuntos_frecuentes.asunto
        """
    )
    return empresas, ingenieros, asuntos



def agregar_empresa(nombre: str):
    execute(
        """
        INSERT INTO empresas (nombre)
        VALUES (%s)
        ON CONFLICT (nombre) DO NOTHING
        """,
        (nombre,),
    )



def agregar_ingeniero(empresa_id: int, titulo: str, nombre: str):
    execute(
        "INSERT INTO ingenieros (empresa_id, titulo, nombre) VALUES (%s, %s, %s)",
        (empresa_id, titulo, nombre),
    )



def agregar_asunto(empresa_id, asunto: str):
    execute(
        "INSERT INTO asuntos_frecuentes (empresa_id, asunto) VALUES (%s, %s)",
        (empresa_id, asunto),
    )



def eliminar_empresa(empresa_id: int):
    execute("DELETE FROM empresas WHERE id = %s", (empresa_id,))



def eliminar_ingeniero(ingeniero_id: int):
    execute("DELETE FROM ingenieros WHERE id = %s", (ingeniero_id,))



def eliminar_asunto(asunto_id: int):
    execute("DELETE FROM asuntos_frecuentes WHERE id = %s", (asunto_id,))
