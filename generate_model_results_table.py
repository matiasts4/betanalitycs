from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT_DIR = Path(__file__).resolve().parent / "Carpeta_Presentacion"
OUTPUT_PNG = OUTPUT_DIR / "14_Tabla_Resultados_Modelos_V8.png"
OUTPUT_CSV = OUTPUT_DIR / "14_Tabla_Resultados_Modelos_V8.csv"
OUTPUT_CHART_PNG = OUTPUT_DIR / "15_Grafico_Resultados_Modelos_V8.png"

MARKET_ORDER = [
    "1X2 (Match Winner)",
    "Double Chance 1X (Home or Draw)",
    "Double Chance X2 (Away or Draw)",
    "Over 2.5 Goals",
    "Under 2.5 Goals",
    "BTTS (Both Teams To Score)",
    "BTTS - No",
    "Home Clean Sheet",
]

MARKET_LABELS = {
    "1X2 (Match Winner)": "1X2 (Ganador)",
    "Double Chance 1X (Home or Draw)": "Doble Oportunidad (1X)",
    "Double Chance X2 (Away or Draw)": "Doble Oportunidad (X2)",
    "Over 2.5 Goals": "Mas de 2.5 Goles",
    "Under 2.5 Goals": "Menos de 2.5 Goles",
    "BTTS (Both Teams To Score)": "Ambos Marcan (BTTS)",
    "BTTS - No": "BTTS - No",
    "Home Clean Sheet": "Valla Invicta Local",
}

MODEL_ORDER = [
    "Logistic Regression",
    "Random Forest",
    "HistGradientBoosting",
    "XGBoost",
]

MODEL_COLORS = {
    "Logistic Regression": "#4c78a8",
    "Random Forest": "#3ecf78",
    "HistGradientBoosting": "#f3c613",
    "XGBoost": "#e45756",
}

RESULT_ROWS = [
    {"market": "1X2 (Match Winner)", "model": "Logistic Regression", "accuracy": 52.30, "roc_auc": None, "f1": 46.93},
    {"market": "1X2 (Match Winner)", "model": "Random Forest", "accuracy": 53.12, "roc_auc": None, "f1": 46.39},
    {"market": "1X2 (Match Winner)", "model": "HistGradientBoosting", "accuracy": 52.06, "roc_auc": None, "f1": 45.97},
    {"market": "1X2 (Match Winner)", "model": "XGBoost", "accuracy": 50.78, "roc_auc": None, "f1": 46.33},
    {"market": "Double Chance 1X (Home or Draw)", "model": "Logistic Regression", "accuracy": 70.32, "roc_auc": 71.38, "f1": 80.10},
    {"market": "Double Chance 1X (Home or Draw)", "model": "Random Forest", "accuracy": 69.68, "roc_auc": 68.18, "f1": 79.87},
    {"market": "Double Chance 1X (Home or Draw)", "model": "HistGradientBoosting", "accuracy": 68.33, "roc_auc": 68.31, "f1": 78.71},
    {"market": "Double Chance 1X (Home or Draw)", "model": "XGBoost", "accuracy": 68.12, "roc_auc": 68.01, "f1": 78.50},
    {"market": "Double Chance X2 (Away or Draw)", "model": "Logistic Regression", "accuracy": 64.43, "roc_auc": 70.54, "f1": 68.36},
    {"market": "Double Chance X2 (Away or Draw)", "model": "Random Forest", "accuracy": 63.90, "roc_auc": 69.16, "f1": 68.54},
    {"market": "Double Chance X2 (Away or Draw)", "model": "HistGradientBoosting", "accuracy": 63.62, "roc_auc": 68.13, "f1": 67.65},
    {"market": "Double Chance X2 (Away or Draw)", "model": "XGBoost", "accuracy": 62.59, "roc_auc": 67.98, "f1": 66.80},
    {"market": "Over 2.5 Goals", "model": "Logistic Regression", "accuracy": 54.72, "roc_auc": 55.35, "f1": 62.32},
    {"market": "Over 2.5 Goals", "model": "Random Forest", "accuracy": 55.28, "roc_auc": 53.97, "f1": 63.84},
    {"market": "Over 2.5 Goals", "model": "HistGradientBoosting", "accuracy": 56.99, "roc_auc": 54.05, "f1": 67.33},
    {"market": "Over 2.5 Goals", "model": "XGBoost", "accuracy": 52.84, "roc_auc": 52.64, "f1": 59.06},
    {"market": "Under 2.5 Goals", "model": "Logistic Regression", "accuracy": 54.72, "roc_auc": 55.35, "f1": 41.99},
    {"market": "Under 2.5 Goals", "model": "Random Forest", "accuracy": 55.25, "roc_auc": 54.34, "f1": 40.76},
    {"market": "Under 2.5 Goals", "model": "HistGradientBoosting", "accuracy": 56.95, "roc_auc": 54.13, "f1": 32.65},
    {"market": "Under 2.5 Goals", "model": "XGBoost", "accuracy": 52.84, "roc_auc": 52.64, "f1": 43.19},
    {"market": "BTTS (Both Teams To Score)", "model": "Logistic Regression", "accuracy": 51.56, "roc_auc": 51.12, "f1": 56.45},
    {"market": "BTTS (Both Teams To Score)", "model": "Random Forest", "accuracy": 50.35, "roc_auc": 49.74, "f1": 57.27},
    {"market": "BTTS (Both Teams To Score)", "model": "HistGradientBoosting", "accuracy": 52.45, "roc_auc": 51.53, "f1": 60.82},
    {"market": "BTTS (Both Teams To Score)", "model": "XGBoost", "accuracy": 51.70, "roc_auc": 51.76, "f1": 55.91},
    {"market": "BTTS - No", "model": "Logistic Regression", "accuracy": 51.56, "roc_auc": 51.12, "f1": 42.12},
    {"market": "BTTS - No", "model": "Random Forest", "accuracy": 51.56, "roc_auc": 49.83, "f1": 38.79},
    {"market": "BTTS - No", "model": "HistGradientBoosting", "accuracy": 53.12, "roc_auc": 50.93, "f1": 34.91},
    {"market": "BTTS - No", "model": "XGBoost", "accuracy": 51.70, "roc_auc": 51.76, "f1": 45.87},
    {"market": "Home Clean Sheet", "model": "Logistic Regression", "accuracy": 69.43, "roc_auc": 60.85, "f1": 22.65},
    {"market": "Home Clean Sheet", "model": "Random Forest", "accuracy": 69.93, "roc_auc": 58.56, "f1": 20.71},
    {"market": "Home Clean Sheet", "model": "HistGradientBoosting", "accuracy": 70.43, "roc_auc": 59.91, "f1": 9.14},
    {"market": "Home Clean Sheet", "model": "XGBoost", "accuracy": 68.33, "roc_auc": 59.82, "f1": 22.98},
]


def build_results_frame() -> pd.DataFrame:
    frame = pd.DataFrame(RESULT_ROWS)
    market_rank = {market: index for index, market in enumerate(MARKET_ORDER)}

    frame["market_order"] = frame["market"].map(market_rank)
    frame["best_by_accuracy"] = frame.groupby("market")["accuracy"].transform("max") == frame["accuracy"]
    frame = frame.sort_values(
        by=["market_order", "best_by_accuracy", "accuracy", "f1"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)

    frame["ROC-AUC"] = frame["roc_auc"].map(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}%")
    frame["Accuracy"] = frame["accuracy"].map(lambda value: f"{value:.2f}%")
    frame["F1"] = frame["f1"].map(lambda value: f"{value:.2f}%")
    frame["Best"] = frame["best_by_accuracy"].map(lambda value: "BEST" if value else "")
    return frame


def render_table(frame: pd.DataFrame) -> None:
    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(20, 16))
    fig.patch.set_facecolor("white")
    ax.axis("off")

    columns = ["Mercado", "Modelo", "Accuracy", "ROC-AUC", "F1", "Best"]
    display = frame.rename(columns={"market": "Mercado", "model": "Modelo"})[columns]

    cell_text = display.values.tolist()
    col_widths = [0.31, 0.24, 0.12, 0.12, 0.10, 0.08]
    table = ax.table(
        cellText=cell_text,
        colLabels=columns,
        colLoc="center",
        cellLoc="center",
        colWidths=col_widths,
        bbox=[0.02, 0.08, 0.96, 0.84],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1, 1.55)

    group_colors = ["#ffffff", "#f3f3f3"]
    current_market = None
    group_index = -1

    for column_index in range(len(columns)):
        header = table[(0, column_index)]
        header.set_facecolor("#404040")
        header.set_text_props(color="white", weight="bold", fontsize=12)
        header.set_edgecolor("#d0d0d0")

    for row_index, (_, row) in enumerate(frame.iterrows(), start=1):
        if row["market"] != current_market:
            current_market = row["market"]
            group_index += 1

        base_color = group_colors[group_index % 2]
        row_color = "#d9f2d9" if row["best_by_accuracy"] else base_color

        for column_index in range(len(columns)):
            cell = table[(row_index, column_index)]
            cell.set_facecolor(row_color)
            cell.set_edgecolor("#d9d9d9")
            if row["best_by_accuracy"]:
                cell.set_text_props(weight="bold")

        market_cell = table[(row_index, 0)]
        model_cell = table[(row_index, 1)]
        market_cell.set_text_props(ha="left")
        model_cell.set_text_props(ha="left")

    fig.suptitle(
        "Resultados Actuales por Mercado y Modelo (V8)\nTabla completa de Accuracy, ROC-AUC y F1",
        fontsize=24,
        fontweight="bold",
        y=0.965,
    )
    fig.text(
        0.02,
        0.03,
        "Fuente: corrida real de train_models.py sobre historical_sanitized_v8.csv (3389 partidos). "
        "ROC-AUC figura como N/A en 1X2 porque el target es multiclase en este evaluador.",
        fontsize=10.5,
        color="#555555",
    )

    fig.savefig(OUTPUT_PNG, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def render_accuracy_chart(frame: pd.DataFrame) -> None:
    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(20, 12))
    fig.patch.set_facecolor("white")

    chart_data = frame[["market", "model", "accuracy", "best_by_accuracy"]].copy()
    market_order = (
        chart_data.groupby("market")["accuracy"]
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )
    chart_data["market"] = pd.Categorical(chart_data["market"], categories=market_order, ordered=True)
    chart_data["model"] = pd.Categorical(chart_data["model"], categories=MODEL_ORDER, ordered=True)
    chart_data = chart_data.sort_values(["market", "model"]).reset_index(drop=True)

    y_positions = np.arange(len(market_order))
    offsets = np.array([-0.27, -0.09, 0.09, 0.27])
    bar_height = 0.16

    for model_index, model_name in enumerate(MODEL_ORDER):
        model_rows = (
            chart_data[chart_data["model"] == model_name]
            .set_index("market")
            .reindex(market_order)
            .reset_index()
        )
        bars = ax.barh(
            y_positions + offsets[model_index],
            model_rows["accuracy"],
            height=bar_height,
            color=MODEL_COLORS[model_name],
            edgecolor="white",
            linewidth=1.0,
            label=model_name,
            zorder=3,
        )

        for bar, (_, row) in zip(bars, model_rows.iterrows()):
            if row["best_by_accuracy"]:
                bar.set_edgecolor("#1f1f1f")
                bar.set_linewidth(2.2)

            ax.text(
                bar.get_width() + 0.55,
                bar.get_y() + bar.get_height() / 2,
                f"{row['accuracy']:.1f}%",
                va="center",
                ha="left",
                fontsize=9.5,
                color="#1f1f1f",
                fontweight="bold" if row["best_by_accuracy"] else "normal",
            )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([MARKET_LABELS[market] for market in market_order], fontsize=15)
    ax.invert_yaxis()
    ax.set_xlim(0, 82)
    ax.set_xlabel("Accuracy de aciertos (%)", fontsize=18, fontweight="bold")
    ax.tick_params(axis="x", labelsize=13)
    ax.grid(axis="x", color="white", linewidth=1.2)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)

    ax.set_title(
        "Comparativa de Accuracy por Mercado y Modelo (V8)\nResultados actuales sobre 3389 partidos reales",
        fontsize=26,
        fontweight="bold",
        pad=22,
    )

    legend = ax.legend(
        title="Modelo",
        loc="lower right",
        fontsize=12,
        title_fontsize=13,
        frameon=True,
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor("#cccccc")

    fig.text(
        0.02,
        0.03,
        "Borde negro = mejor accuracy dentro de cada mercado. Fuente: train_models.py con TimeSeriesSplit sobre historical_sanitized_v8.csv.",
        fontsize=10.5,
        color="#555555",
    )

    fig.savefig(OUTPUT_CHART_PNG, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = build_results_frame()
    export_columns = ["market", "model", "accuracy", "roc_auc", "f1", "best_by_accuracy"]
    frame[export_columns].to_csv(OUTPUT_CSV, index=False)
    render_table(frame)
    render_accuracy_chart(frame)

    print(f"Tabla PNG generada en: {OUTPUT_PNG}")
    print(f"Tabla CSV generada en: {OUTPUT_CSV}")
    print(f"Grafico PNG generado en: {OUTPUT_CHART_PNG}")


if __name__ == "__main__":
    main()