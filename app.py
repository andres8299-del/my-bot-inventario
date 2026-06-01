import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# CONFIGURACIÓN BÁSICA
st.set_page_config(layout="wide")
st.title("Sistema de Inventario")

# URL DE TU HOJA (Asegúrate de que sea pública)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

def cargar_datos(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        
        # Limpieza de nombres de columnas
        data.columns = data.columns.str.strip()
        
        # MAPEO ESTRICTO DE 4 COLUMNAS
        # Asignamos nombres fijos según el orden para evitar errores de lectura
        nuevos_nombres = {
            data.columns[0]: "Codigo",
            data.columns[1]: "Descripcion",
            data.columns[2]: "Disponible",
            data.columns[3]: "Precio"
        }
        data = data.rename(columns=nuevos_nombres)
        
        # Limpieza de datos: quitar espacios y asegurar números
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
    # MOSTRAR TABLA SIMPLE
    st.write("### Inventario Actual")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("---")

    # CHATBOT DE CONSULTA
    st.write("### Consultar Producto")
    if prompt := st.chat_input("Escribe el código o nombre del producto"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            # Buscamos en 'Codigo' y 'Descripcion' para que sea más inteligente
            opciones = df['Codigo'].tolist() + df['Descripcion'].tolist()
            mejor_coincidencia, puntuacion = process.extractOne(prompt, opciones, scorer=fuzz.token_sort_ratio)
            
            if puntuacion > 50:
                # Encontrar a qué fila pertenece la coincidencia
                fila = df[(df['Codigo'] == mejor_coincidencia) | (df['Descripcion'] == mejor_coincidencia)].iloc[0]
                
                # Mostrar resultados planos
                st.write(f"**Código:** {fila['Codigo']}")
                st.write(f"**Descripción:** {fila['Descripcion']}")
                st.write(f"**Disponible:** {int(fila['Disponible'])} unidades")
                st.write(f"**Precio:** ${fila['Precio']:,}")
            else:
                st.write("No se encontró información para esa búsqueda.")
else:
    st.warning("Introduce la URL de Google Sheets en el código.")
