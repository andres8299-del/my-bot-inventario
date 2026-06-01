import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Sistema de Inventario Pro", layout="wide")

st.title("📊 Panel de Control e Inventario")
st.markdown("---")

# ENLACE DE TU HOJA (Asegúrate de que sea pública)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

try:
    # Transformar link para lectura directa
    csv_url = URL_HOJA.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
    
    # Cargar datos
    df = pd.read_csv(csv_url)
    # Limpiar espacios en blanco de los nombres de columnas
    df.columns = df.columns.str.strip()

    # --- PARTE 1: VISUALIZACIÓN ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Tabla de Stock")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 Gráfico de Niveles")
        # Creamos una gráfica de barras: X = Producto, Y = Cantidad
        st.bar_chart(df.set_index("Producto")["Cantidad"])

    # --- PARTE 2: CHATBOT ---
    st.markdown("---")
    st.subheader("💬 Asistente Virtual")
    
    if prompt := st.chat_input("¿Qué deseas consultar?"):
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            query = prompt.lower()
            # Buscar el producto en el DataFrame
            resultado = df[df['Producto'].str.contains(query, case=False, na=False)]
            
            if not resultado.empty:
                prod = resultado.iloc[0]['Producto']
                cant = resultado.iloc[0]['Cantidad']
                st.write(f"El producto **{prod}** tiene **{cant}** unidades disponibles.")
                if cant < 10:
                    st.warning("⚠️ ¡Atención! Este producto tiene stock bajo.")
            else:
                st.write("Hola. Puedo decirte cuántas unidades hay de un producto. Intenta escribiendo el nombre de uno.")

except Exception as e:
    st.error("Error al conectar. Revisa que el link de Google Sheets sea público y el formato sea correcto.")
