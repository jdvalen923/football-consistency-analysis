import pandas as pd
import os
import glob

def fusionar_excels_tfg():
    directorio = os.path.dirname(os.path.abspath(__file__))
    archivos_excel = glob.glob(os.path.join(directorio, "TFG_R*.xlsx"))
    
    if not archivos_excel:
        print("❌ No files found to join.")
        return

    print(f"📂 Found {len(archivos_excel)} matches.")

    lista_df = []
    for f in archivos_excel:
        df_temp = pd.read_excel(f)
        # Cleaning: eliminate empty rows because of errors
        df_temp = df_temp.dropna(subset=['Name', 'Rating'])
        lista_df.append(df_temp)

    df_maestro = pd.concat(lista_df, ignore_index=True)

    # Ensure Round is numeric
    if df_maestro['Round'].dtype == object:
        df_maestro['Round'] = df_maestro['Round'].astype(str).str.extract('(\d+)').astype(int)

    df_maestro = df_maestro.sort_values(by=['Round', 'Team', 'Name'])

    # Save file
    nombre_final = "DATABASE_TFG_FINAL.xlsx"
    ruta_final = os.path.join(directorio, nombre_final)
    df_maestro.to_excel(ruta_final, index=False)
    
    print(f"✅ Done! {len(archivos_excel)} files.")

if __name__ == "__main__":
    fusionar_excels_tfg()