import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# CONFIGURACIÓN
st.set_page_config(page_title="Inventario Preciso", layout="wide")
st.title("📦 Sistema de Inventario de Alta Precisión")

# URL DE TU HOJA (Reemplaza con tu link)
URL_HOJA = "TU_ENLACE_AQUI"

@st.cache_data(ttl=30)
def cargar_datos(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        data = data.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # Mapeo por posición: 0:Codigo, 1:Descripcion, 2:Disponible, 3:Precio
        mapeo = {
            data.columns[0]: "Codigo",
            data.columns[1]: "Descripcion",
            data.columns[2]: "Disponible",
            data.columns[3]: "Precio"
        }
        data = data.rename(columns=mapeo)
        
        # Limpieza de textos
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
    # --- MÉTRICAS GENERALES ---
    v_total = (df['Disponible'] * df['Precio']).sum()
    st.metric("Valor Total en Bodega", f"${v_total:,.0f}")

    # --- TABLA ---
    with st.expander("Ver base de datos completa"):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("---")

    # --- CHATBOT DE ALTA PRECISIÓN ---
    st.subheader("💬 Buscador de Productos")
    if prompt := st.chat_input("Escribe el nombre o código..."):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            query = prompt.strip().lower()
            
            # 1. BÚSQUEDA POR CONTENIDO
            mask = (df['Codigo'].str.lower().str.contains(query, na=False)) | \
                   (df['Descripcion'].str.lower().str.contains(query, na=False))
            
            res = df[mask]
            
            if not res.empty:
                st.write(f"✅ Se encontraron **{len(res)}** productos:")
                for _, fila in res.iterrows():
                    # Cálculo del valor del stock específico
                    valor_stock = fila['Disponible'] * fila['Precio']
                    
                    # Diseño de la respuesta con métricas visuales
                    with st.container():
                        st.markdown(f"### 📍 {fila['Descripcion']}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Precio Unitario", f"${fila['Precio']:,.0f}")
                        c2.metric("Disponible", f"{int(fila['Disponible'])} und")
                        c3.metric("Valor en Stock", f"${valor_stock:,.0f}")
                        st.caption(f"Código de referencia: {fila['Codigo']}")
                        st.write("---")
            else:
                # 2. SUGERENCIAS SI NO HAY COINCIDENCIA EXACTA
                opciones = df['Descripcion'].tolist()
                sugerencias = process.extract(prompt, opciones, scorer=fuzz.token_set_ratio, limit=3)
                sugerencias_validas = [s for s in sugerencias if s[1] > 45]
                
                if sugerencias_validas:
                    st.warning(f"No encontré '{prompt}'. Quizás buscabas:")
                    for nombre_sug, score in sugerencias_validas:
                        fila_sug = df[df['Descripcion'] == nombre_sug].iloc[0]
                        # Botón rápido para ver info de la sugerencia
                        if st.button(f"Ver info de: {nombre_sug}"):
                            st.info(f"**{nombre_sug}** | Stock: {int(fila_sug['Disponible'])} | Precio: ${fila_sug['Precio']:,.0f}")
                else:
                    st.error("❌ No se encontró ningún producto con ese nombre o código.")

else:
    st.warning("Configura tu URL de Google Sheets en el código.")
