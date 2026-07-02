import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw_architecture_diagram():
    # Configuración de estilo
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    
    # Fondo suave
    fig.patch.set_facecolor('#F7FAFC')
    ax.set_facecolor('#F7FAFC')
    
    # -------------------------------------------------------------
    # DIBUJAR BLOQUES
    # -------------------------------------------------------------
    
    # Bloque 1: Entrada de Datos
    box_data = patches.FancyBboxPatch((0.5, 3.75), 2.0, 1.5, boxstyle="round,pad=0.1", 
                                      facecolor='#EDF2F7', edgecolor='#CBD5E0', linewidth=1.5)
    ax.add_patch(box_data)
    ax.text(1.5, 4.5, "DATOS DE ENTRADA\n(Fixtures, ELO,\nFatiga, Cuotas)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#4A5568')
    
    # Bloque 2: Modelo Principal (Capa 1)
    box_l1 = patches.FancyBboxPatch((3.2, 3.25), 2.4, 2.5, boxstyle="round,pad=0.1", 
                                    facecolor='#EBF8FF', edgecolor='#4299E1', linewidth=2.0)
    ax.add_patch(box_l1)
    ax.text(4.4, 4.8, "CAPA 1: MODELO PRINCIPAL\n(XGBoost / Optuna)", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#2B6CB0')
    ax.text(4.4, 3.8, "[ESTIMACIÓN DE PROBABILIDAD]\nEstima p(Local), p(Empate), etc.\nCalibración Isotónica\n(No se modifica)", 
            ha='center', va='center', fontsize=8, color='#2D3748', style='italic')
    
    # Bloque 3: Filtro EV Dinámico (Capa 3)
    box_l3 = patches.FancyBboxPatch((6.3, 5.0), 2.5, 2.2, boxstyle="round,pad=0.1", 
                                    facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=2.0)
    ax.add_patch(box_l3)
    ax.text(7.55, 6.4, "CAPA 3: EV DINÁMICO\n(Filtro de Varianza)", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#9B2C2C')
    ax.text(7.55, 5.7, "EV >= EV_min * max(1, sqrt(c-1))\nExcluye apuestas con\nretorno insuficiente para su riesgo", 
            ha='center', va='center', fontsize=8, color='#2D3748')
    
    # Bloque 4: Meta-Labeling (Capa 2)
    box_l2 = patches.FancyBboxPatch((6.3, 1.8), 2.5, 2.2, boxstyle="round,pad=0.1", 
                                    facecolor='#FFFAF0', edgecolor='#DD6B20', linewidth=2.0)
    ax.add_patch(box_l2)
    ax.text(7.55, 3.2, "CAPA 2: META-LABELING\n(Filtro de Falsos Positivos)", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#DD6B20')
    ax.text(7.55, 2.4, "Random Forest Walk-Forward\nEvalúa contexto (fatiga, ELO)\nAutoriza solo si p(win) >= 50%", 
            ha='center', va='center', fontsize=8, color='#2D3748')
    
    # Bloque 5: Destinos Finales
    # Aprobado
    box_ok = patches.FancyBboxPatch((9.7, 3.0), 1.8, 1.2, boxstyle="round,pad=0.1", 
                                    facecolor='#F0FFF4', edgecolor='#38A169', linewidth=2.0)
    ax.add_patch(box_ok)
    ax.text(10.6, 3.6, "APUESTA APROBADA\n(Ejecución en mercado)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#22543D')
    
    # Rechazado
    box_no = patches.FancyBboxPatch((9.7, 5.2), 1.8, 1.2, boxstyle="round,pad=0.1", 
                                    facecolor='#F7FAFC', edgecolor='#A0AEC0', linewidth=1.5)
    ax.add_patch(box_no)
    ax.text(10.6, 5.8, "APUESTA FILTRADA\n(Evita pérdida)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#4A5568')
    
    # -------------------------------------------------------------
    # CONECTORES (FLECHAS)
    # -------------------------------------------------------------
    
    # Datos -> L1
    ax.annotate("", xy=(3.1, 4.5), xytext=(2.6, 4.5),
                arrowprops=dict(arrowstyle="-|>", color='#718096', lw=2, mutation_scale=15))
    
    # L1 -> L3 (Filtro EV)
    ax.annotate("", xy=(6.2, 6.1), xytext=(5.7, 4.7),
                arrowprops=dict(arrowstyle="-|>", color='#4299E1', lw=2, mutation_scale=15, 
                                connectionstyle="angle,angleA=0,angleB=90,rad=10"))
    ax.text(5.5, 5.7, "Cuota + Prob", fontsize=8, color='#2B6CB0', fontweight='bold')
    
    # L3 -> L2 (Si pasa EV)
    ax.annotate("", xy=(7.55, 4.1), xytext=(7.55, 4.9),
                arrowprops=dict(arrowstyle="-|>", color='#E53E3E', lw=2, mutation_scale=15))
    ax.text(7.7, 4.5, "Pasa EV\n(Candidata)", fontsize=8, color='#9B2C2C', fontweight='bold', va='center')
    
    # L3 -> Rechazada (Si NO pasa EV)
    ax.annotate("", xy=(9.6, 5.8), xytext=(8.9, 6.1),
                arrowprops=dict(arrowstyle="-|>", color='#E53E3E', lw=1.5, ls='--', mutation_scale=12,
                                connectionstyle="angle,angleA=0,angleB=90,rad=5"))
    ax.text(9.25, 6.3, "No pasa", fontsize=8, color='#A0AEC0')
    
    # L2 -> Aprobada (Si es autorizada)
    ax.annotate("", xy=(9.6, 3.6), xytext=(8.9, 2.9),
                arrowprops=dict(arrowstyle="-|>", color='#38A169', lw=2, mutation_scale=15,
                                connectionstyle="angle,angleA=0,angleB=-90,rad=5"))
    ax.text(9.25, 2.5, "Autorizada", fontsize=8, color='#22543D', fontweight='bold')
    
    # L2 -> Rechazada (Si NO es autorizada)
    ax.annotate("", xy=(10.6, 5.1), xytext=(8.9, 2.9),
                arrowprops=dict(arrowstyle="-|>", color='#A0AEC0', lw=1.5, ls='--', mutation_scale=12,
                                connectionstyle="angle3,angleA=0,angleB=90"))
    ax.text(9.7, 4.6, "No autorizada\n(Falso Positivo)", fontsize=8, color='#A0AEC0', ha='center')
    
    # -------------------------------------------------------------
    # TEXTOS EXPLICATIVOS E INTEGRIDAD
    # -------------------------------------------------------------
    
    # Línea divisoria de integridad
    ax.plot([6.0, 6.0], [0.5, 8.5], color='#718096', linestyle=':', alpha=0.5, linewidth=1.5)
    ax.text(5.9, 8.3, "MODELO PRINCIPAL (INTACTO)", ha='right', va='center', fontsize=8, color='#718096', fontweight='bold')
    ax.text(6.1, 8.3, "MOTOR DE GESTIÓN DE DECISIONES (POST-PROCESAMIENTO)", ha='left', va='center', fontsize=8, color='#718096', fontweight='bold')
    
    # Título del Diagrama
    ax.text(6.0, 8.7, "Flujo de Trabajo del Sistema Dual de Decisión (BetAnalytics)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1A202C')
    
    plt.tight_layout()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "47_Arquitectura_Sistema_Dual.png"))
    plt.savefig(output_path, dpi=300, facecolor='#F7FAFC', bbox_inches='tight')
    plt.close()
    print(f"[OK] Diagrama de arquitectura guardado en: {output_path}")

if __name__ == '__main__':
    draw_architecture_diagram()
