import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# CONFIGURACIÓN
st.set_page_config(page_title="Bot Inventario Inteligente", layout="wide")
st.title("🤖 Asistente de Inventario Inteligente")

URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

def cargar_datos(url):
    try:
        # Convertir link a CSV
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        
        # --- LIMPIEZA PROFUNDA DE COLUMNAS ---
        data.columns = data.columns.str.strip()
        if len(data.columns) >= 2:
            data = data.rename(columns={data.columns[0]: "Producto", data.columns[1]: "Cantidad"})
        
        # --- LIMPIEZA PROFUNDA DE DATOS ---
        # Eliminamos espacios en blanco al inicio/final de los nombres de productos
        data['Producto'] = data['Producto'].astype(str).str.strip()
        # Aseguramos que la cantidad sea numérica
        data['Cantidad'] = pd.to_numeric(data['Cantidad'], errors='coerce').fillna(0)
        
        # Quitamos filas que tengan el producto vacío
        data = data[data['Producto'] != "nan"]
        
        return data
    except Exception as e:
        st.error(f"Error al leer la hoja: {e}")
        return None

df = cargar_datos(URL_HOJA)

if df is not None:
    lista_productos = df['Producto'].tolist()

    # --- BARRA LATERAL (OPCIONES) ---
    st.sidebar.header("🔍 Buscador")
    seleccion = st.sidebar.selectbox("Selecciona de la lista:", [""] + lista_productos)
    if seleccion:
        stock = df[df['Producto'] == seleccion]['Cantidad'].values[0]
        st.sidebar.metric(label=f"Stock de {seleccion}", value=int(stock))

    # --- VISUALIZACIÓN ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Inventario")
        st.dataframe(df, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("📊 Gráfico")
        st.bar_chart(df.set_index("Producto")["Cantidad"])

    # --- CHATBOT CORREGIDO ---
    st.markdown("---")
    st.subheader("💬 Consulta al Bot")
    
    if prompt := st.chat_input("¿Qué producto buscas?"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            # Limpiar la entrada del usuario
            entrada_usuario = prompt.strip()
            
            # 1. INTENTO DE COINCIDENCIA EXACTA (Ignorando mayúsculas/minúsculas)
            coincidencia_directa = df[df['Producto'].str.lower() == entrada_usuario.lower()]
            
            if not coincidencia_directa.empty:
                nombre = coincidencia_directa.iloc[0]['Producto']
                stock = coincidencia_directa.iloc[0]['Cantidad']
                st.write(f"✅ Encontrado: Hay **{int(stock)}** unidades de **{nombre}**.")
            
            else:
                # 2. SI NO ES EXACTO, USAR LÓGICA DIFUSA
                mejor_coincidencia, puntuacion = process.extractOne(
                    entrada_usuario, 
                    lista_productos, 
                    scorer=fuzz.token_sort_ratio
                )
                
                if puntuacion > 50: # Umbral de confianza
                    fila = df[df['Producto'] == mejor_coincidencia]
                    stock = fila['Cantidad'].values[0]
                    
                    st.write(f"No encontré exactamente '{entrada_usuario}', pero quizás quisiste decir: **{mejor_coincidencia}**.")
                    st.write(f"📦 El stock de **{mejor_coincidencia}** es de **{int(stock)}** unidades.")
                else:
                    st.write("❌ No logré encontrar ese producto. Intenta usar palabras más cortas o revisa la tabla de arriba.")

else:
    st.error("Revisa que el link de Google Sheets sea público y el código tenga la URL correcta.")
