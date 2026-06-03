import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# CONFIGURACIÓN
st.set_page_config(page_title="Inventario Preciso", layout="wide")
st.title("📦 Sistema de Inventario de Alta Precisión")

# URL DE TU HOJA (Reemplaza con tu link)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

@st.cache_data(ttl=30)
def cargar_datos(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        data = data.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # Mapeo por posición (Código, Descripción, Disponible, Precio)
        mapeo = {
            data.columns[0]: "Codigo",
            data.columns[1]: "Descripcion",
            data.columns[2]: "Disponible",
            data.columns[3]: "Precio"
        }
        data = data.rename(columns=mapeo)
        
        # Limpieza absoluta de textos
        for col in ['Codigo', 'Descripcion']:
            data[col] = data[col].astype(str).str.strip()
            
        # Limpieza de números
        data['Disponible'] = pd.to_numeric(data['Disponible'], errors='coerce').fillna(0)
        data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0)
        
        return data
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df = cargar_datos(URL_HOJA)

if df is not None:
    # --- MÉTRICAS ---
    v_total = (df['Disponible'] * df['Precio']).sum()
    st.metric("Valor del Almacén", f"${v_total:,.0f}")

    # --- TABLA ---
    st.write("### Base de Datos")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("---")

    # --- CHATBOT DE ALTA PRECISIÓN ---
    st.subheader("💬 Buscador Exacto")
    if prompt := st.chat_input("Escribe el nombre o código del producto..."):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            query = prompt.strip().lower()
            
            # 1. BUSQUEDA POR CONTENIDO (Exactitud total)
            # Filtra si el texto aparece en el Código o en la Descripción
            mask = (df['Codigo'].str.lower().str.contains(query, na=False)) | \
                   (df['Descripcion'].str.lower().str.contains(query, na=False))
            
            resultados_exactos = df[mask]
            
            if not resultados_exactos.empty:
                st.write(f"✅ He encontrado {len(resultados_exactos)} coincidencia(s):")
                for _, fila in resultados_exactos.iterrows():
                    with st.expander(f"📍 {fila['Descripcion']} (Ver detalles)", expanded=True):
                        st.markdown(f"""
                        **Código:** `{fila['Codigo']}`  
                        **Stock:** {int(fila['Disponible'])} unidades  
                        **Precio:** ${fila['Precio']:,}  
                        **Subtotal:** ${fila['Disponible'] * fila['Precio']:,}
                        """)
            else:
                # 2. BÚSQUEDA POR SUGERENCIAS (Si escribió con errores)
                opciones = df['Descripcion'].tolist()
                # Obtenemos las 3 mejores sugerencias
                sugerencias = process.extract(prompt, opciones, scorer=fuzz.token_set_ratio, limit=3)
                
                # Solo mostrar si la puntuación es decente (>40)
                sugerencias_validas = [s for s in sugerencias if s[1] > 40]
                
                if sugerencias_validas:
                    st.write(f"No encontré exactamente '{prompt}'. ¿Tal vez buscas alguno de estos?")
                    for nombre_sug, score in sugerencias_validas:
                        fila_sug = df[df['Descripcion'] == nombre_sug].iloc[0]
                        if st.button(f"Ver {nombre_sug}", key=fila_sug['Codigo']):
                            st.write(f"**Código:** {fila_sug['Codigo']} | **Stock:** {int(fila_sug['Disponible'])}")
                else:
                    st.error("❌ No se encontraron productos. Intenta con otra palabra clave.")

else:
    st.warning("Verifica el enlace de tu Google Sheets.")
