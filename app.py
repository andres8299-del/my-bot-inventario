import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Sistema de Gestión de Inventario", layout="wide")
st.title("📦 Control de Inventario e Inteligencia de Negocio")

# URL DE TU HOJA (Reemplaza con tu link de Google Sheets)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

def cargar_datos(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        
        # Limpieza de nombres de columnas por posición
        data.columns = data.columns.str.strip()
        nuevos_nombres = {
            data.columns[0]: "Codigo",
            data.columns[1]: "Descripcion",
            data.columns[2]: "Disponible",
            data.columns[3]: "Precio"
        }
        data = data.rename(columns=nuevos_nombres)
        
        # Limpieza de datos y conversión numérica
        data['Codigo'] = data['Codigo'].astype(str).str.strip()
        data['Descripcion'] = data['Descripcion'].astype(str).str.strip()
        data['Disponible'] = pd.to_numeric(data['Disponible'], errors='coerce').fillna(0)
        data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0)
        
        return data
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df = cargar_datos(URL_HOJA)

if df is not None:
    # --- SECCIÓN 1: MÉTRICAS DE NEGOCIO ---
    valor_total = (df['Disponible'] * df['Precio']).sum()
    productos_bajos = df[df['Disponible'] < 5] # Alerta si hay menos de 5 unidades

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="💰 Valor Total del Inventario", value=f"${valor_total:,.0f}")
    with col2:
        st.metric(label="⚠️ Productos en Alerta (Stock Bajo)", value=len(productos_bajos))

    if not productos_bajos.empty:
        with st.expander("Ver productos por agotarse"):
            st.write(productos_bajos[['Descripcion', 'Disponible']])

    st.write("---")

    # --- SECCIÓN 2: TABLA DE DATOS ---
    st.write("### Inventario Actual")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("---")

    # --- SECCIÓN 3: CHATBOT DE CONSULTA ---
    st.write("### 💬 Asistente de Consultas")
    if prompt := st.chat_input("Escribe el código o descripción del producto"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            # Buscamos en Código y Descripción
            opciones = df['Codigo'].tolist() + df['Descripcion'].tolist()
            mejor_coincidencia, puntuacion = process.extractOne(prompt, opciones, scorer=fuzz.token_sort_ratio)
            
            if puntuacion > 50:
                # Localizar la fila de la coincidencia
                fila = df[(df['Codigo'] == mejor_coincidencia) | (df['Descripcion'] == mejor_coincidencia)].iloc[0]
                
                # Respuesta detallada
                st.write(f"**Resultado para:** {mejor_coincidencia}")
                st.markdown(f"""
                - **Código:** {fila['Codigo']}
                - **Descripción:** {fila['Descripcion']}
                - **Disponible:** {int(fila['Disponible'])} unidades
                - **Precio Unitario:** ${fila['Precio']:,}
                - **Valor en Stock:** ${fila['Disponible'] * fila['Precio']:,}
                """)
            else:
                st.write("No logré identificar el producto. Intenta ser más específico.")
else:
    st.warning("Introduce la URL pública de Google Sheets en el código.")
