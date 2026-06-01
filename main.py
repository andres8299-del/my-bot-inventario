import streamlit as st
from st_gsheets_connection import GSheetsConnection

st.title("🤖 Bot de Inventario")

# Conectar con Google Sheets
url = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"
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
