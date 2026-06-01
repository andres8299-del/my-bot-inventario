import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# CONFIGURACIÓN
st.set_page_config(page_title="Bot Inventario Inteligente", layout="wide")
st.title("🤖 Asistente de Inventario con Descripción")

# ⚠️ PEGA TU ENLACE AQUÍ
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

def cargar_datos(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        
        # Limpieza de nombres de columnas
        data.columns = data.columns.str.strip()
        
        # MAPEO INTELIGENTE:
        # Asumimos: Columna 0 = Producto, Columna 1 = Cantidad, Columna 2 = Descripción
        nuevos_nombres = {}
        if len(data.columns) >= 1: nuevos_nombres[data.columns[0]] = "Producto"
        if len(data.columns) >= 2: nuevos_nombres[data.columns[1]] = "Cantidad"
        if len(data.columns) >= 3: nuevos_nombres[data.columns[2]] = "Descripcion"
        
        data = data.rename(columns=nuevos_nombres)
        
        # Limpieza de datos
        data['Producto'] = data['Producto'].astype(str).str.strip()
        if 'Descripcion' in data.columns:
            data['Descripcion'] = data['Descripcion'].astype(str).str.strip().replace('nan', 'Sin descripción')
        data['Cantidad'] = pd.to_numeric(data['Cantidad'], errors='coerce').fillna(0)
        
        return data
    except Exception as e:
        st.error(f"Error al conectar: {e}")
        return None

df = cargar_datos(URL_HOJA)

if df is not None:
    lista_productos = df['Producto'].tolist()

    # --- VISUALIZACIÓN ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📋 Inventario Completo")
        st.dataframe(df, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("📊 Niveles de Stock")
        st.bar_chart(df.set_index("Producto")["Cantidad"])

    # --- CHATBOT CON DESCRIPCIÓN ---
    st.markdown("---")
    st.subheader("💬 Consulta detalles del producto")
    
    if prompt := st.chat_input("¿Qué producto buscas?"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            entrada = prompt.strip()
            
            # Buscador inteligente (Fuzzy)
            mejor_coincidencia, puntuacion = process.extractOne(
                entrada, lista_productos, scorer=fuzz.token_sort_ratio
            )
            
            if puntuacion > 50:
                fila = df[df['Producto'] == mejor_coincidencia].iloc[0]
                nombre = fila['Producto']
                stock = int(fila['Cantidad'])
                
                # Verificar si existe la columna descripción
                desc = fila['Descripcion'] if 'Descripcion' in fila else "No disponible"
                
                st.write(f"### {nombre}")
                st.write(f"📦 **Stock:** {stock} unidades")
                st.write(f"📝 **Descripción:** {desc}")
                
                if stock < 5:
                    st.error("⚠️ ¡Quedan muy pocas unidades!")
            else:
                st.write("❌ No encontré un producto similar. Revisa la tabla superior.")
else:
    st.warning("Configura el enlace de Google Sheets en el código.")
