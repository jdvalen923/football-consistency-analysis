import pandas as pd
import os

def limpieza_profunda_tfg_mismo_excel():
    directorio = os.path.dirname(os.path.abspath(__file__))
    archivo_bd = os.path.join(directorio, "DATABASE_TFG_FINAL.xlsx")
    
    # 1. Load both sheets in same Excel file
    # 'Sheet1' DATABASE y 'Sheet3' LIST
    df_maestro = pd.read_excel(archivo_bd, sheet_name='Sheet1') 
    df_lista_1000 = pd.read_excel(archivo_bd, sheet_name='Sheet3') 

    print(f"Initial registers in database: {len(df_maestro)}")

    # Filter 1: +1000 minutes played 
    nombres_validos = df_lista_1000['Name'].dropna().unique()
    df_filtrado = df_maestro[df_maestro['Name'].isin(nombres_validos)]
    print(f"Filter 1: {df_filtrado['Name'].nunique()} players detected.")

    # Filter 2: Eliminate GK
    df_filtrado = df_filtrado[df_filtrado['Position'] != 'GK']
    print(f"Filter 2: {df_filtrado['Name'].nunique()}.")

    # Filter 3: Only matches with >= 30 minutes played
    df_filtrado = df_filtrado[df_filtrado['Minutes played'] >= 30]
    print(f"Filter 3:  {len(df_filtrado)}.")

    # Save results in another excel
    nombre_final = "DATABASE_TFG_FINAL_PROCESSED.xlsx"
    df_filtrado.to_excel(os.path.join(directorio, nombre_final), index=False)
    
    print(f"\nDone!")

if __name__ == "__main__":
    limpieza_profunda_tfg_mismo_excel()