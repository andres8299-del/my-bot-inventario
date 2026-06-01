import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestor de Inventario Pro", layout="wide")

# Estilo personalizado para que se vea profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 Sistema de Control de Inventario Inteligente")
st.info("Conectado en tiempo real con Google Sheets")

# 2. COLOCA AQUÍ TU ENLACE DE GOOGLE SHEETS
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

def cargar_datos(url):
    # Transformación universal de URL a formato de datos (CSV)
    try:
        if "/edit" in url:
            base_url = url.split("/edit")[0]
            csv_url = f"{base_url}/export?format=csv"
        else:
            csv_url = url
        
        data = pd.read_csv(csv_url)
        # Limpieza automática de nombres de columnas
        data.columns = data.columns.str.strip()
        
        # Adaptación Universal: Forzamos nombres internos para que el código no falle
        # Independientemente de cómo los escribas en Excel, el código los entenderá
        if len(data.columns) >= 2:
            data = data.rename(columns={data.columns[0]: "Producto", data.columns[1]: "Cantidad"})
        
        return data
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# 3. EJECUCIÓN Y VISUALIZACIÓN
df = cargar_datos(https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing)

if df is not None:
    # Dividir la pantalla en dos columnas
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📋 Inventario Actual")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("📈 Análisis Visual de Stock")
        try:
            # Creamos la gráfica usando los nombres adaptados
            st.bar_chart(df.set_index("Producto")["Cantidad"])
        except:
            st.warning("Asegúrate de que la segunda columna de tu Excel tenga números.")

    st.markdown("---")

    # 4. CHATBOT ADAPTATIVO
    st.subheader("💬 Asistente de Consultas")
    
    if prompt := st.chat_input("¿Qué producto deseas consultar?"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            texto = prompt.lower()
            # Buscamos en la columna "Producto" (que ya adaptamos arriba)
            busqueda = df[df['Producto'].astype(str).str.contains(texto, case=False, na=False)]
            
            if not busqueda.empty:
                p = busqueda.iloc[0]['Producto']
                c = busqueda.iloc[0]['Cantidad']
                st.write(f"He revisado la base de datos: del producto **{p}** actualmente tenemos **{c}** unidades.")
                
                if c < 5:
                    st.error("⚠️ ALERTA: Stock críticamente bajo.")
                elif c < 20:
                    st.warning("⚠️ NOTA: Stock próximo a agotarse.")
            else:
                st.write("No encuentro ese producto exacto. ¿Podrías verificar el nombre?")
else:
    st.warning("Esperando conexión con la base de datos... Revisa el enlace en el código.")
