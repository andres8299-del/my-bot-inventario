import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Inventario Inteligente", layout="wide")
st.title("🚀 Sistema de Inventario Adaptativo")

# URL DE TU HOJA (Reemplaza con tu link)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

@st.cache_data(ttl=60) # Esto hace que la búsqueda sea ultra rápida al cachear datos por 1 min
def cargar_datos(url):
    try:
        # Conversión de URL
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        
        # ELIMINAR COLUMNAS VACÍAS (Si las hay)
        data = data.dropna(how='all', axis=1)
        
        # ADAPTACIÓN AUTOMÁTICA POR POSICIÓN
        # No importa cómo se llamen en Excel, el bot las mapea así:
        mapeo = {
            data.columns[0]: "Codigo",
            data.columns[1]: "Descripcion",
            data.columns[2]: "Disponible",
            data.columns[3]: "Precio"
        }
        data = data.rename(columns=mapeo)
        
        # LIMPIEZA DE DATOS (Strip elimina espacios invisibles)
        for col in ['Codigo', 'Descripcion']:
            data[col] = data[col].astype(str).str.strip()
            
        # CONVERSIÓN NUMÉRICA SEGURA
        data['Disponible'] = pd.to_numeric(data['Disponible'], errors='coerce').fillna(0)
        data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0)
        
        return data
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")
        return None

df = cargar_datos(URL_HOJA)

if df is not None:
    # --- MÉTRICAS RÁPIDAS ---
    valor_total = (df['Disponible'] * df['Precio']).sum()
    st.metric("Valor Total Inventario", f"${valor_total:,.0f}")

    # --- TABLA DE DATOS ---
    st.write("### Vista General")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("---")

    # --- CHATBOT ADAPTATIVO ---
    st.subheader("💬 Buscador Inteligente")
    st.info("Puedes escribir el código o una parte de la descripción (ej: 'aceite', 'fil', 'A102').")
    
    if prompt := st.chat_input("¿Qué producto buscas hoy?"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            query = prompt.strip().lower()
            
            # 1. BÚSQUEDA RÁPIDA (Coincidencias exactas o contenidas)
            resultado = df[
                (df['Codigo'].str.lower().str.contains(query)) | 
                (df['Descripcion'].str.lower().str.contains(query))
            ]
            
            if not resultado.empty:
                for _, fila in resultado.head(3).iterrows(): # Mostramos hasta 3 coincidencias
                    st.success(f"**{fila['Descripcion']}**")
                    st.markdown(f"""
                    - **Código:** `{fila['Codigo']}`
                    - **Stock:** {int(fila['Disponible'])} unidades
                    - **Precio:** ${fila['Precio']:,}
                    """)
            else:
                # 2. BÚSQUEDA CONFIABLE (Si escribió mal, usamos Lógica Difusa)
                opciones = df['Descripcion'].tolist() + df['Codigo'].tolist()
                mejor_match, score = process.extractOne(prompt, opciones, scorer=fuzz.token_sort_ratio)
                
                if score > 55:
                    # Buscamos la fila que corresponde a ese match
                    fila_difusa = df[(df['Descripcion'] == mejor_match) | (df['Codigo'] == mejor_match)].iloc[0]
                    st.write(f"No encontré '{prompt}', pero encontré algo muy parecido:")
                    st.info(f"**{fila_difusa['Descripcion']}** (Código: {fila_difusa['Codigo']})")
                    st.write(f"Disponible: {int(fila_difusa['Disponible'])} | Precio: ${fila_difusa['Precio']:,}")
                else:
                    st.write("❌ No se encontraron productos similares. Intenta con otra palabra.")

else:
    st.warning("⚠️ Esperando enlace de Google Sheets...")
