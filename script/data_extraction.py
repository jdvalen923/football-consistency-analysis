import json
import pandas as pd
import os
import re

#https://www.sofascore.com/api/v1/event/12437726/lineups
def procesar_tfg_final():
    # --- Match configuration ---
    jornada_input = "38"
    resultado_local = "L"   #(W, D, L)
    h_name = "Athletic Club"      
    a_name = "Barcelona"   
       
    # ---------------------------------
    match = re.search(r'\d+', jornada_input)
    jornada_num = int(match.group()) if match else jornada_input

    directorio = os.path.dirname(os.path.abspath(__file__))
    archivo_entrada = os.path.join(directorio, 'datos.json')
    
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            data = json.load(f)

        lista_jugadores = []

        for equipo_key in ['home', 'away']:
            es_home = (equipo_key == 'home')
            current_side = data.get(equipo_key, {})
            
            equipo_actual = h_name if es_home else a_name
            rival_actual = a_name if es_home else h_name
            res = resultado_local if es_home else ("L" if resultado_local == "W" else "W" if resultado_local == "L" else "D")

            for p in current_side.get('players', []):
                s = p.get('statistics', {})
                pi = p.get('player', {})
                mins = s.get('minutesPlayed', 0)
                
                # Base metrics
                t_w_i = s.get('wonTackle', 0) + s.get('interceptionWon', 0)
                clears = s.get('totalClearance', 0) + s.get('clearanceOffLine', 0)
                kp = s.get('keyPass', 0)
                sot = s.get('onTargetScoringAttempt', 0)
                xg = s.get('expectedGoals', 0)
                
                def per_90(stat):
                    return round((stat / mins) * 90, 2) if mins > 0 else 0

                registro = {
                    'Name': pi.get('name', 'Unknown'),
                    'Team': equipo_actual,
                    'Age': pi.get('age', 'N/A'),
                    'Position': {'G':'GK','D':'DF','M':'MF','F':'FW'}.get(pi.get('position',''), pi.get('position','')),
                    'Round': jornada_num, 
                    'Venue': "Home" if es_home else "Away",
                    'Opponent': rival_actual,
                    'Result': res,
                    'Minutes played': mins,
                    'Rating': s.get('rating', 0),
                    'T+I Total': t_w_i,
                    'Clearances': clears,
                    'PassAcc%': round((s.get('accuratePass', 0)/s.get('totalPass', 1)*100), 2) if s.get('totalPass', 0) > 0 else 0,
                    'KeyPass': kp,
                    'SoT': sot,
                    'xG': xg,
                    'T+I_90': per_90(t_w_i),
                    'Clearances_90': per_90(clears),
                    'KeyPass_90': per_90(kp),
                    'SoT_90': per_90(sot),
                    'xG_90': per_90(xg)
                }
                lista_jugadores.append(registro)

        df = pd.DataFrame(lista_jugadores)
        nombre_archivo = f"TFG_R{jornada_num}_{h_name}_vs_{a_name}".replace(" ", "_") + ".xlsx"
        df.to_excel(os.path.join(directorio, nombre_archivo), index=False)
        
        print(f"✅ Excel generated (Venue {jornada_num}): {nombre_archivo}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    procesar_tfg_final()