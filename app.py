import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="Bot Inventario Inteligente", layout="wide")

st.title("🤖 Asistente de Inventario Inteligente")
st.markdown("---")

# 2. ENLACE DE TU HOJA (Cámbialo por el tuyo)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

def cargar_datos(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drivesdk', '/export?format=csv')
        data = pd.read_csv(csv_url)
        data.columns = data.columns.str.strip()
        # Forzar nombres de columnas internos
        if len(data.columns) >= 2:
            data = data.rename(columns={data.columns[0]: "Producto", data.columns[1]: "Cantidad"})
        return data
    except:
        return None

df = cargar_datos(URL_HOJA)

if df is not None:
    # --- BARRA LATERAL CON OPCIONES (AUTOCOMPLETADO) ---
    st.sidebar.header("🔍 Buscador Rápido")
    lista_productos = df['Producto'].tolist()
    seleccion = st.sidebar.selectbox("Selecciona un producto de la lista:", [""] + lista_productos)

    if seleccion:
        stock = df[df['Producto'] == seleccion]['Cantidad'].values[0]
        st.sidebar.success(f"Stock de {seleccion}: {stock} unidades.")

    # --- CUERPO PRINCIPAL: TABLA Y GRÁFICA ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📋 Lista Total")
        st.dataframe(df, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("📊 Visualización")
        st.bar_chart(df.set_index("Producto")["Cantidad"])

    st.markdown("---")

    # --- CHATBOT CON LÓGICA DIFUSA (FUZZY LOGIC) ---
    st.subheader("💬 Chatea con el Inventario")
    st.write("*Puedes escribir con errores o solo una parte del nombre.*")
    
    if prompt := st.chat_input("Ej: ¿Cuantos flltros hay?"):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            # 1. Buscar coincidencia exacta o parcial
            # 2. Usar 'thefuzz' para encontrar el nombre más parecido
            mejor_coincidencia, puntuacion = process.extractOne(prompt, lista_productos, scorer=fuzz.partial_token_set_ratio)
            
            if puntuacion > 60: # Si se parece en más de un 60%
                fila = df[df['Producto'] == mejor_coincidencia]
                nombre_real = fila['Producto'].values[0]
                cantidad = fila['Cantidad'].values[0]
                
                if puntuacion < 95:
                    st.write(f"No encontré '{prompt}', pero quizás quisiste decir: **{nombre_real}**.")
                
                st.write(f"📦 El stock de **{nombre_real}** es de **{cantidad}** unidades.")
                
                if cantidad < 10:
                    st.error("⚠️ ¡Quedan pocas unidades!")
            else:
                st.write("No logré encontrar nada parecido. Prueba seleccionando el producto en el menú de la izquierda.")
else:
    st.error("Error de conexión. Verifica que el link sea público.")
