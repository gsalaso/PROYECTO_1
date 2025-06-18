import pandas as pd
import streamlit as st
import io

st.title("Procesador de Horarios Académicos")

# Subida de archivo
archivo = st.file_uploader("Carga tu archivo CSV", type=["csv"])

if archivo is not None:
    # Leer CSV
    df = pd.read_csv(archivo)

    # Conversión segura a enteros
    df['HORAS'] = pd.to_numeric(df['HORAS'], errors='coerce').fillna(0).astype(int)
    df['HT'] = pd.to_numeric(df['HT'], errors='coerce').fillna(0).astype(int)
    df['HP'] = pd.to_numeric(df['HP'], errors='coerce').fillna(0).astype(int)

    # Lista para almacenar resultados
    filas_repetidas = []

    # PARTE 1: Solo para TIPO distinto de NORMAL (repetir por HORAS)
    df_otros = df[df['TIPO'] != 'NORMAL']
    for _, row in df_otros.iterrows():
        for _ in range(row['HORAS']):
            fila = row.copy()
            fila['ORIGEN'] = 'HORAS'
            filas_repetidas.append(fila)

    # PARTE 2: Para filas con TIPO = NORMAL (usar HT y HP)
    df_normal = df[df['TIPO'] == 'NORMAL']
    for _, fila_normal in df_normal.iterrows():
        cod_curso = fila_normal['COD CURSO']

        for _ in range(fila_normal['HT']):
            fila_ht = fila_normal.copy()
            fila_ht['ORIGEN'] = 'NORMAL_HT'
            filas_repetidas.append(fila_ht)

        fila_practica = df[(df['TIPO'] == 'PRACTICA') & (df['COD CURSO'] == cod_curso)]
        if not fila_practica.empty:
            tipo_horario_practica = fila_practica.iloc[0]['TIPO HORARIO']
            for _ in range(fila_normal['HP']):
                fila_hp = fila_normal.copy()
                fila_hp['TIPO HORARIO'] = tipo_horario_practica
                fila_hp['ORIGEN'] = 'NORMAL_HP'
                filas_repetidas.append(fila_hp)

    # Crear DataFrame final
    df_repetido = pd.DataFrame(filas_repetidas)

    # Orden personalizado para columna TIPO
    orden_tipo = ['NORMAL', 'TEORIA', 'PRACTICA']
    df_repetido['TIPO'] = pd.Categorical(df_repetido['TIPO'], categories=orden_tipo, ordered=True)
    df_repetido = df_repetido.sort_values(by=['COD CURSO', 'TIPO'])

    st.success("Procesamiento completo. Revisa la tabla resultante:")
    st.dataframe(df_repetido)

    # Descargar archivo
    output = io.BytesIO()
    df_repetido.to_csv(output, index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Descargar archivo procesado",
        data=output.getvalue(),
        file_name='resultado_final.csv',
        mime='text/csv'
    )
