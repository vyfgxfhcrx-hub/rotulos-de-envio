import subprocess
import sys

# 📦 Verificar e instalar reportlab si falta
try:
    import reportlab
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    import reportlab

import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import tempfile
import os

# 📁 Buscar cliente en Excel
def obtener_nombre_cliente(codigo_cliente, df_clientes):
    if 'codigo' in df_clientes.columns and 'nombre' in df_clientes.columns:
        cliente = df_clientes[df_clientes['codigo'] == codigo_cliente]
        if not cliente.empty:
            return cliente.iloc[0]['nombre']
    return None

# 🧾 Generar etiquetas PDF
def generar_etiquetas(nombre_cliente, facturas, cantidad_bultos, ruta_pdf):
    etiquetas_por_hoja = 8
    ancho, alto = A4
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    margen_x = 20 * mm
    margen_y = 20 * mm
    espacio_vertical = (alto - 2 * margen_y) / 4
    espacio_horizontal = (ancho - 2 * margen_x) / 2

    for i in range(cantidad_bultos):
        fila = (i % etiquetas_por_hoja) // 2
        columna = (i % etiquetas_por_hoja) % 2
        x = margen_x + columna * espacio_horizontal
        y = alto - margen_y - fila * espacio_vertical

        c.setFont("Helvetica-Bold", 20)
        c.drawString(x, y, f"Cliente: {nombre_cliente}")
        c.setFont("Helvetica", 20)
        c.drawString(x, y - 20, f"Factura(s): {', '.join(facturas)}")
        c.drawString(x, y - 40, f"Bulto {i + 1} de {cantidad_bultos}")

        if (i + 1) % etiquetas_por_hoja == 0:
            c.showPage()

    c.save()

# 🚀 Interfaz Streamlit
st.title("Generador de Rótulos de Envío 📦")

archivo_excel = st.file_uploader("📁 Cargar archivo Excel de clientes", type=["xls", "xlsx"])
codigo_cliente = st.text_input("🔢 Código de cliente")

nombre_cliente = None
if archivo_excel and codigo_cliente:
    try:
        df_clientes = pd.read_excel(archivo_excel)
        nombre_cliente = obtener_nombre_cliente(codigo_cliente, df_clientes)
        if not nombre_cliente:
            nombre_cliente = st.text_input("✍️ Cliente no encontrado. Ingrese el nombre manualmente:")
        else:
            st.success(f"Cliente encontrado: {nombre_cliente}")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        nombre_cliente = st.text_input("✍️ Ingrese el nombre del cliente manualmente:")

elif codigo_cliente:
    nombre_cliente = st.text_input("✍️ Ingrese el nombre del cliente manualmente:")

facturas_input = st.text_input("🧾 Ingrese hasta 4 números de factura separados por coma")
facturas = [f.strip() for f in facturas_input.split(",") if f.strip()][:4]

cantidad_bultos = st.number_input("📦 Cantidad de bultos", min_value=1, step=1)

if st.button("🎯 Generar etiquetas") and nombre_cliente and facturas and cantidad_bultos:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        generar_etiquetas(nombre_cliente, facturas, cantidad_bultos, tmp.name)
        st.success("✅ Etiquetas generadas correctamente.")
        st.download_button("📥 Descargar PDF", data=open(tmp.name, "rb").read(), file_name="etiquetas_envio.pdf", mime="application/pdf")
        os.unlink(tmp.name)