import pandas as pd
import streamlit as st
import io

st.title("Procesador de Horarios Académicos")

archivo = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if archivo is not None:
    df = pd.read_csv(archivo)

    df['HORAS'] = pd.to_numeric(df['HORAS'], errors='coerce').fillna(0).astype(int)
    df['HT'] = pd.to_numeric(df['HT'], errors='coerce').fillna(0).astype(int)
    df['HP'] = pd.to_numeric(df['HP'], errors='coerce').fillna(0).astype(int)

    filas_repetidas = []

    # No-NORMAL → repetir por HORAS
    df_otros = df[df['TIPO'] != 'NORMAL']
    for _, row in df_otros.iterrows():
        for _ in range(row['HORAS']):
            fila = row.copy()
            fila['ORIGEN'] = 'HORAS'
            filas_repetidas.append(fila)

    # NORMAL → HT y HP
    df_normal = df[df['TIPO'] == 'NORMAL']
    for _, fila_normal in df_normal.iterrows():
        cod_curso = fila_normal['COD CURSO']
        ht = fila_normal['HT']
        hp = fila_normal['HP']

        if ht > 0:
            for _ in range(ht):
                fila_ht = fila_normal.copy()
                fila_ht['ORIGEN'] = 'NORMAL_HT'
                filas_repetidas.append(fila_ht)

        if hp > 0:
            fila_practica = df[(df['TIPO'] == 'PRACTICA') & (df['COD CURSO'] == cod_curso)]
            if not fila_practica.empty:
                tipo_horario_practica = fila_practica.iloc[0]['TIPO HORARIO']
            else:
                tipo_horario_practica = fila_normal['TIPO HORARIO']

            for _ in range(hp):
                fila_hp = fila_normal.copy()
                fila_hp['TIPO HORARIO'] = tipo_horario_practica
                fila_hp['ORIGEN'] = 'NORMAL_HP'
                filas_repetidas.append(fila_hp)

    df_repetido = pd.DataFrame(filas_repetidas)

    orden_tipo = ['NORMAL', 'TEORIA', 'PRACTICA']
    df_repetido['TIPO'] = pd.Categorical(df_repetido['TIPO'], categories=orden_tipo, ordered=True)
    df_repetido = df_repetido.sort_values(by=['COD CURSO', 'TIPO'])

    st.success("✅ Procesamiento completado")
    st.dataframe(df_repetido)

    output = io.BytesIO()
    df_repetido.to_csv(output, index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Descargar CSV procesado",
        data=output.getvalue(),
        file_name="resultado_corregido.csv",
        mime="text/csv"
    )

