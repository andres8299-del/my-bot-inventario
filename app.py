import streamlit as st
import pandas as pd

st.title("📦 Mi Inventario Gratis")

# COPIA TU ENLACE AQUÍ
# Ejemplo: https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing
URL_HOJA = "https://docs.google.com/spreadsheets/d/1AI95MtHQAAYazuhEGusW0W7R8c-dXGBqQgjRDSwQvhU/edit?usp=sharing"

try:
    # Este truco transforma el link de compartir en un link de datos puros
    csv_url = URL_HOJA.replace('/edit?usp=sharing', '/export?format=csv')
    
    # El bot lee la hoja de cálculo
    df = pd.read_csv(csv_url)
    
    st.write("### Inventario en tiempo real:")
    st.dataframe(df)
    
    # Chat de consulta
    query = st.chat_input("¿Qué producto buscas?")
    if query:
        with st.chat_message("user"):
            st.write(query)
        
        # Lógica simple de búsqueda
        resultado = df[df['Producto'].str.contains(query, case=False, na=False)]
        
        with st.chat_message("assistant"):
            if not resultado.empty:
                st.write(f"Encontré esto: {resultado.iloc[0]['Cantidad']} unidades.")
            else:
                st.write("No encuentro ese producto en la lista.")

except Exception as e:
    st.warning("Pega el enlace de tu hoja arriba para empezar.")
