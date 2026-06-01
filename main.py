import streamlit as st
from st_gsheets_connection import GSheetsConnection

st.title("🤖 Bot de Inventario")

# Conectar con Google Sheets
url = "TU_URL_DE_GOOGLE_SHEETS_AQUI"
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos
df = conn.read(spreadsheet=url, usecols=[0, 1])
df = df.dropna()

# Mostrar Inventario
st.subheader("Inventario Actual")
st.table(df)

# Chat simple
prompt = st.chat_input("Escribe: sumar Clavos 20")

if prompt:
    st.write(f"Has pedido: {prompt}")
    st.info("Para procesar cambios, conectaremos la edición en el siguiente paso.")
