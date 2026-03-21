import sqlite3

def init_db():
    conn = sqlite3.connect("cotizaciones.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_referencia TEXT NOT NULL,
            fecha TEXT NOT NULL,
            empresa TEXT NOT NULL,
            ingeniero TEXT,
            asunto TEXT NOT NULL,
            total_numero REAL NOT NULL,
            total_letras TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            pdf_nombre TEXT
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos creada correctamente.")