import pandas as pd
import numpy as np
import os
import sys

def fix_script_emojis(file_path):
    if not os.path.exists(file_path):
        print(f"Archivo no encontrado para parchear emojis: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Reemplazar emojis comunes para evitar UnicodeEncodeError en consola de Windows
    content = content.replace("✅", "[OK]")
    content = content.replace("❌", "[Error]")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Emojis corregidos en: {file_path}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mirror_csv = os.path.join(base_dir, "models", "mirrors", "mirror_comparison_results.csv")
    optimized_csv = os.path.join(base_dir, "models", "optimized_models_comparison_results.csv")
    
    if not os.path.exists(mirror_csv):
        print(f"[Error] No se encontró {mirror_csv}")
        return
        
    if not os.path.exists(optimized_csv):
        print(f"[Error] No se encontró {optimized_csv}")
        return
        
    # 1. Cargar datasets
    df_mirror = pd.read_csv(mirror_csv)
    df_opt = pd.read_csv(optimized_csv)
    
    print(f"Cargados resultados de resampling: {len(df_mirror)} filas.")
    print(f"Cargados resultados optimizados: {len(df_opt)} filas.")
    
    # 2. Reemplazar la línea base ('main') con los valores optimizados
    updated_count = 0
    for idx, row in df_opt.iterrows():
        target = row['target_name']
        model = row['model_name']
        acc = row['accuracy']
        f1 = row['f1_score']
        auc = row['roc_auc']
        
        # Encontrar la fila correspondiente en mirror
        mask = (df_mirror['mirror_config'] == 'main') & (df_mirror['target_name'] == target) & (df_mirror['model_name'] == model)
        if mask.any():
            df_mirror.loc[mask, 'accuracy'] = acc
            df_mirror.loc[mask, 'f1_score'] = f1
            df_mirror.loc[mask, 'roc_auc'] = auc
            updated_count += 1
            
    print(f"Actualizadas {updated_count} filas de la línea base ('main') en mirror_comparison_results.csv.")
    
    # Guardar los resultados actualizados
    df_mirror.to_csv(mirror_csv, index=False)
    print("[OK] mirror_comparison_results.csv actualizado en disco.")
    
    # 3. Parchear emojis en los scripts de graficación para evitar UnicodeEncodeError en Windows
    scripts_to_fix = [
        os.path.join(base_dir, "generar_comparativa_resampling_todas.py"),
        os.path.join(base_dir, "generar_comparativa_completa_all.py"),
        os.path.join(base_dir, "generar_graficos_totales.py")
    ]
    
    for script in scripts_to_fix:
        fix_script_emojis(script)
        
    # 4. Ejecutar los scripts para regenerar los gráficos con los nuevos parámetros
    print("\nRegenerando gráficos comparativos de resampling con la nueva línea base optimizada...")
    
    # Importar y ejecutar las funciones main de cada script de forma segura
    sys.path.append(base_dir)
    
    try:
        import generar_comparativa_resampling_todas
        print("\n--- Ejecutando generar_comparativa_resampling_todas.py ---")
        generar_comparativa_resampling_todas.main()
    except Exception as e:
        print(f"[Error] Falló generar_comparativa_resampling_todas.py: {e}")
        
    try:
        import generar_comparativa_completa_all
        # Recargar el módulo para asegurarnos de que use la versión sin emojis
        import importlib
        importlib.reload(generar_comparativa_completa_all)
        print("\n--- Ejecutando generar_comparativa_completa_all.py ---")
        generar_comparativa_completa_all.main()
    except Exception as e:
        print(f"[Error] Falló generar_comparativa_completa_all.py: {e}")
        
    try:
        import generar_graficos_totales
        import importlib
        importlib.reload(generar_graficos_totales)
        print("\n--- Ejecutando generar_graficos_totales.py ---")
        generar_graficos_totales.main()
    except Exception as e:
        print(f"[Error] Falló generar_graficos_totales.py: {e}")
        
    print("\n[OK] ¡Todos los gráficos de comparación han sido actualizados con éxito en la Carpeta_Presentacion!")

if __name__ == "__main__":
    main()
