import pandas as pd
import numpy as np
import unicodedata
import os
import matplotlib.pyplot as plt


class CONTENEDOR:

# funcion general para cargar excel o csv
    def cargar_excel(self, path):
        df_incidentes = pd.read_csv(path)
        return df_incidentes
    
# funcion general para analisis de informacion principal de la base
    def analizar(self, df):

        print("INFORMACIÓN GENERAL")
        print("=" * 60)

        print(f"Filas: {df.shape[0]}")
        print(f"Columnas: {df.shape[1]}")

        print("\nNombres de columnas:")
        print(df.columns.tolist())

        print("\nTipos de datos:")
        print(df.dtypes.to_string())

        print("\nPrimeras 5 filas:")
        print(df.head().to_string())

        print("\nÚltimas 5 filas:")
        print(df.tail().to_string())

        print("\n--- INFO DEL DATAFRAME ---")
        df.info()

        return df

# tratamiento general de valores nulos en la base de datos
    def analizar_nulos(self, df):

        if df is None:
            raise ValueError("El DataFrame recibido es None.")

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Se esperaba un DataFrame y se recibió: {type(df)}")

        nulos = df.isnull()

        total_filas = len(df)
        total_columnas = len(df.columns)
        total_nulos = nulos.sum().sum()

        filas_con_nulos = nulos.any(axis=1).sum()

        porcentaje_filas_afectadas = round(
            (filas_con_nulos / total_filas) * 100, 2
        )

        resumen = pd.DataFrame({
            "Nulos": nulos.sum(),
            "% Nulos": round(nulos.mean() * 100, 2)
        })

        resumen = resumen[resumen["Nulos"] > 0]

        if len(resumen) > 0:
            resumen = resumen.sort_values(
                by="% Nulos",
                ascending=False
            )

        print("\n" + "=" * 70)
        print("ANÁLISIS DE VALORES NULOS")
        print("=" * 70)

        print(f"Total registros: {total_filas:,}")
        print(f"Total columnas: {total_columnas:,}")
        print(f"Total valores nulos: {total_nulos:,}")

        if total_nulos == 0:
            print("\n✅ No se encontraron valores nulos.")
            print("=" * 70)
            return df

        print("\nColumnas con valores nulos:")
        print(resumen.to_string())

        columnas_vacias = resumen[
            resumen["% Nulos"] == 100
        ]

        print("\nColumnas completamente vacías:")

        if len(columnas_vacias) > 0:
            print(columnas_vacias.index.tolist())
        else:
            print("Ninguna")

        columnas_mas_50 = resumen[
            resumen["% Nulos"] > 50
        ]

        print("\nColumnas con más del 50% de nulos:")

        if len(columnas_mas_50) > 0:
            print(columnas_mas_50.to_string())
        else:
            print("Ninguna")

        print("\nTop 10 columnas con más nulos:")
        print(resumen.head(10).to_string())

        print(f"\nFilas con al menos un nulo: {filas_con_nulos:,}")

        print(
            f"Porcentaje de filas afectadas: "
            f"{porcentaje_filas_afectadas}%"
        )

        print("=" * 70)

        return df

# funcion general para normalizacion de valores categoricos y numericos
    def normalizar(self, df):

        if df is None:
            raise ValueError("El DataFrame recibido es None")

        def quitar_tildes(texto):
            if pd.isna(texto):
                return texto

            texto = str(texto)

            return "".join(
                c for c in unicodedata.normalize("NFD", texto)
                if unicodedata.category(c) != "Mn"
            )

        nuevas_columnas = []

        for col in df.columns:

            col = quitar_tildes(col)

            col = col.lower().strip()

            col = col.replace(" ", "_")
            col = col.replace("-", "_")
            col = col.replace("/", "_")
            col = col.replace("\\", "_")
            col = col.replace(".", "_")
            col = col.replace(",", "_")
            col = col.replace("(", "")
            col = col.replace(")", "")

            while "__" in col:
                col = col.replace("__", "_")

            nuevas_columnas.append(col)

        df.columns = nuevas_columnas

        columnas_texto = df.select_dtypes(
            include=["object"]
        ).columns

        for col in columnas_texto:

            df[col] = (
                df[col]
                .astype(str)
                .apply(quitar_tildes)
                .str.lower()
                .str.strip()
                .str.replace(r"\s+", "_", regex=True)
            )

        # ==========================================
        # NORMALIZAR VARIABLES NUMÉRICAS
        # ==========================================

        columnas_numericas = df.select_dtypes(
            include=["int64", "float64", "int32", "float32"]
        ).columns

        for col in columnas_numericas:

            minimo = df[col].min()
            maximo = df[col].max()

            if maximo != minimo:
                df[col] = (df[col] - minimo) / (maximo - minimo)
            else:
                df[col] = 0

        print("=" * 60)
        print("NORMALIZACION COMPLETADA")
        print("=" * 60)

        return df
# funcion general para analisis descriptivo de una base de datos
    def analisis_descriptivo(self, df):

        if df is None:
            raise ValueError("El DataFrame recibido es None.")

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Se esperaba un DataFrame y se recibió: {type(df)}")

        print("\n" + "=" * 80)
        print("ANÁLISIS DESCRIPTIVO GENERAL")
        print("=" * 80)

        print(f"\nTotal de registros: {df.shape[0]:,}")
        print(f"Total de columnas: {df.shape[1]:,}")

        columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

        columnas_categoricas = df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        print("\nVariables numéricas encontradas:")
        if len(columnas_numericas) > 0:
            print(columnas_numericas)
        else:
            print("No hay variables numéricas.")

        print("\nVariables categóricas encontradas:")
        if len(columnas_categoricas) > 0:
            print(columnas_categoricas)
        else:
            print("No hay variables categóricas.")

        if len(columnas_numericas) > 0:
            print("\n" + "-" * 80)
            print("ESTADÍSTICAS DESCRIPTIVAS - VARIABLES NUMÉRICAS")
            print("-" * 80)

            descriptivo_numerico = df[columnas_numericas].describe().T.copy()

            descriptivo_numerico["mediana"] = df[columnas_numericas].median()
            descriptivo_numerico["varianza"] = df[columnas_numericas].var()
            descriptivo_numerico["asimetria"] = df[columnas_numericas].skew()
            descriptivo_numerico["curtosis"] = df[columnas_numericas].kurtosis()
            descriptivo_numerico["nulos"] = df[columnas_numericas].isnull().sum()
            descriptivo_numerico["%_nulos"] = round(
                df[columnas_numericas].isnull().mean() * 100, 2
            )

            print(descriptivo_numerico.to_string())

        if len(columnas_categoricas) > 0:
            print("\n" + "-" * 80)
            print("ESTADÍSTICAS DESCRIPTIVAS - VARIABLES CATEGÓRICAS")
            print("-" * 80)

            descriptivo_categorico = pd.DataFrame({
                "variable": columnas_categoricas,
                "valores_unicos": [
                    df[col].nunique(dropna=True)
                    for col in columnas_categoricas
                ],
                "nulos": [
                    df[col].isnull().sum()
                    for col in columnas_categoricas
                ],
                "%_nulos": [
                    round(df[col].isnull().mean() * 100, 2)
                    for col in columnas_categoricas
                ],
                "moda": [
                    df[col].mode(dropna=True).iloc[0]
                    if not df[col].mode(dropna=True).empty
                    else None
                    for col in columnas_categoricas
                ],
                "frecuencia_moda": [
                    df[col].value_counts(dropna=True).iloc[0]
                    if not df[col].value_counts(dropna=True).empty
                    else 0
                    for col in columnas_categoricas
                ]
            })

            print(descriptivo_categorico.to_string(index=False))

            print("\nTop 10 valores por variable categórica:")

            for col in columnas_categoricas:
                print("\n" + "-" * 60)
                print(f"Variable: {col}")
                print("-" * 60)
                print(df[col].value_counts(dropna=False).head(10).to_string())

        if len(columnas_numericas) >= 2:
            print("\n" + "-" * 80)
            print("MATRIZ DE CORRELACIÓN - VARIABLES NUMÉRICAS")
            print("-" * 80)

            matriz_correlacion = df[columnas_numericas].corr()

            print(matriz_correlacion.to_string())

        else:
            print("\nNo hay suficientes variables numéricas para calcular matriz de correlación.")

        print("\n" + "=" * 80)
        print("ANÁLISIS DESCRIPTIVO FINALIZADO")
        print("=" * 80)

        return df
            
        
# funcion general para estadistica general de una base de datos
    def estadistica(self, df):

        if df is None:
            raise ValueError("El DataFrame recibido es None.")

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Se esperaba un DataFrame y se recibió: {type(df)}")

        print("\n" + "=" * 70)
        print("ESTADÍSTICA DESCRIPTIVA GENERAL")
        print("=" * 70)

        print(f"\nTotal de registros: {df.shape[0]:,}")
        print(f"Total de columnas: {df.shape[1]:,}")

        print("\nTipos de datos:")
        print(df.dtypes.to_string())

        columnas_numericas = df.select_dtypes(
            include=[np.number]
        ).columns

        columnas_categoricas = df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns

        print("\nVariables numéricas:")
        print(list(columnas_numericas) if len(columnas_numericas) > 0 else "No hay variables numéricas.")

        print("\nVariables categóricas:")
        print(list(columnas_categoricas) if len(columnas_categoricas) > 0 else "No hay variables categóricas.")

        if len(columnas_numericas) > 0:
            print("\nResumen estadístico de variables numéricas:")
            print(df[columnas_numericas].describe().T.to_string())

        if len(columnas_categoricas) > 0:
            print("\nResumen estadístico de variables categóricas:")
            print(df[columnas_categoricas].describe().T.to_string())

        print("\n" + "=" * 70)
        print("FIN DE LA ESTADÍSTICA DESCRIPTIVA GENERAL")
        print("=" * 70)

        return df
    


# funcion general para guardar archivo excel 
    def guardar_excel(self, df, nombre_archivo):
       
        if df is None:
            raise ValueError(
                "El DataFrame recibido es None."
            )

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"Se esperaba un DataFrame y se recibió: {type(df)}"
            )

        nombre_base, extension = os.path.splitext(nombre_archivo)

        nuevo_nombre = f"{nombre_base}_1{extension}"

        df.to_excel(
            nuevo_nombre,
            index=False
        )

        print("\n" + "=" * 60)
        print("ARCHIVO EXCEL GUARDADO CORRECTAMENTE")
        print("=" * 60)
        print(f"Archivo: {nuevo_nombre}")
        print(f"Registros: {df.shape[0]:,}")
        print(f"Columnas: {df.shape[1]:,}")
        print("=" * 60)

        return df