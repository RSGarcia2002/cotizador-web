from flask import Flask, render_template
from datetime import datetime, timedelta
import os

app = Flask(__name__)

ARCHIVO_CORRELATIVO = "correlativo.txt"

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

    if not os.path.exists(ARCHIVO_CORRELATIVO):
        with open(ARCHIVO_CORRELATIVO, "w", encoding="utf-8") as archivo:
            archivo.write("1")
        correlativo = 1
    else:
        with open(ARCHIVO_CORRELATIVO, "r", encoding="utf-8") as archivo:
            contenido = archivo.read().strip()
            correlativo = int(contenido) if contenido.isdigit() else 1

    return f"NT-{anio}-{correlativo:04d}"

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

    return render_template(
        "index.html",
        fecha=fecha,
        validez=validez,
        no_referencia=no_referencia,
        datos_fijos=datos_fijos
    )

if __name__ == "__main__":
    app.run(debug=True)