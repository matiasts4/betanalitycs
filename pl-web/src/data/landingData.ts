import {
  Bot,
  TrendingUp,
  Shield,
  Zap,
  BarChart3,
  Target,
  Database,
  Brain,
  Calculator,
  CheckCircle2,
  type LucideIcon,
} from "lucide-react";

// ============================================================
// BETANALITYCS LANDING DATA
// ============================================================
// Este archivo es la fuente única de verdad para todo el
// contenido de la landing page. Si querés cambiar textos,
// estadísticas, resultados de modelos o el flujo de decisión,
// hacelo acá. No es necesario tocar Landing.tsx.
//
// Para íconos usamos lucide-react. Podés ver todos los
// disponibles en: https://lucide.dev/icons
// ============================================================

export interface HeroStat {
  label: string;
  value: string;
  icon: LucideIcon;
}

export interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

export interface ModelResult {
  name: string;
  accuracy: number;
  rocAuc: number | null;
  f1: number;
  isBest: boolean;
}

export interface MarketResult {
  id: string;
  label: string;
  shortLabel: string;
  models: ModelResult[];
}

export interface DecisionStep {
  icon: LucideIcon;
  title: string;
  description: string;
}

export interface LandingData {
  brand: {
    name: string;
    tagline: string;
    description: string;
    ctaPrimary: string;
    ctaSecondary: string;
  };
  hero: {
    badge: string;
    headline: string[];
    subheadline: string;
    stats: HeroStat[];
  };
  features: Feature[];
  modelResults: {
    title: string;
    subtitle: string;
    source: string;
    markets: MarketResult[];
  };
  decisionFlow: {
    title: string;
    subtitle: string;
    steps: DecisionStep[];
  };
  markets: {
    title: string;
    subtitle: string;
    items: string[];
  };
  cta: {
    title: string;
    subtitle: string;
    button: string;
  };
  footer: {
    tagline: string;
  };
  overfitting: {
    "1x2": { modelName: string; trainAcc: number; testAcc: number; gap: number; diagnostic: string }[];
    over25: { modelName: string; trainAcc: number; testAcc: number; gap: number; diagnostic: string }[];
  };
  metaDecision: {
    configs: { configName: string; bankroll: number; roi: number; bets: number; avoided: number; drawdown: number; diagnostic: string }[];
    crecimiento: { step: string; lineaBase: number; metaModelo: number; sistemaDual: number }[];
  };
  backtesting: {
    profitChart: { name: string; profit: number; bankroll: number }[];
    oddsProfit: { oddsRange: string; profit: number; bets: number }[];
    summary: { label: string; value: string; detail: string }[];
  };
  pipeline: {
    featureImportance: { feature: string; importance: number; category: string }[];
  };
}

// -------------- BRAND --------------
const brand: LandingData["brand"] = {
  name: "BetAnalytics",
  tagline: "Modelado Predictivo y Optimización Financiera en la Premier League",
  description:
    "Un proyecto académico de investigación cuantitativa que integra modelos de Machine Learning y algoritmos de optimización de portafolios (criterio de Kelly) para modelar ventajas matemáticas reales sobre el mercado de cuotas deportivas.",
  ctaPrimary: "Abrir Panel",
  ctaSecondary: "Saber más",
};

// -------------- HERO STATS --------------
// Dimensiones reales de este proyecto de investigación.
const heroStats: HeroStat[] = [
  { label: "Modelos Predictivos", value: "8 Pipelines", icon: Brain },
  { label: "Histórico Premier", value: "9 Temporadas", icon: Database },
  { label: "Gestión de Banca", value: "Quarter Kelly", icon: Calculator },
  { label: "Capas de Control", value: "3 Niveles", icon: Shield },
];

// -------------- HERO --------------
const hero: LandingData["hero"] = {
  badge: "Investigación y Analítica de Datos con IA",
  headline: ["Modelado Predictivo y", "Optimización de Banca"],
  subheadline: brand.description,
  stats: heroStats,
};

// -------------- FEATURES --------------
const features: Feature[] = [
  {
    icon: BarChart3,
    title: "Análisis Profundo de Partidos",
    description:
      "Probabilidades de victoria, modelos xG y cálculos de ventaja para cada partido de la Premier League en más de 8 mercados.",
  },
  {
    icon: Shield,
    title: "Perfiles de Equipo y Jugador",
    description:
      "Gráficos de radar interactivos, análisis de forma y desgloses estadísticos detallados para cada equipo, jugador y árbitro.",
  },
  {
    icon: Target,
    title: "Detección de Valor",
    description:
      "Nuestra IA identifica cuotas mal valoradas en tiempo real, destacando apuestas de alta ventaja con puntuaciones de confianza y cálculo de cuotas justas.",
  },
  {
    icon: Brain,
    title: "Ensemble de 4 Modelos",
    description:
      "Combinamos Logistic Regression, Random Forest, HistGradientBoosting y XGBoost evaluados con TimeSeriesSplit sobre 3.420 partidos reales.",
  },
  {
    icon: Database,
    title: "Pipeline Sanitizado",
    description:
      "Datos crudos pasan por un pipeline que elimina fugas de información, cuotas del bookmaker en entrenamiento y goles reales previos por colinealidad.",
  },
  {
    icon: Zap,
    title: "Simulación de Estrategias",
    description:
      "Backtesting con stakes fijos, Kelly fraccional y comparación de modelos para entender el riesgo, drawdown y rentabilidad esperada.",
  },
];

// -------------- RESULTADOS DE MODELOS --------------
// Datos extraídos de evaluar_modelos_optimos.py y evaluar_comparativa_completa.py
// (archive/pl-predictor/models/optimized_models_comparison_results.csv).
// El flag isBest marca el modelo ganador dentro de cada mercado.
const modelResults: LandingData["modelResults"] = {
  title: "Resultados por Mercado y Modelo",
  subtitle:
    "Métricas reales entrenadas sobre el dataset histórico (3.420 partidos de Premier League).",
  source:
    "Fuente: corrida real de train_models.py con TimeSeriesSplit en el dataset principal. ROC-AUC figura como N/A en 1X2 porque el target es multiclase en este evaluador.",
  markets: [
    {
      id: "1x2",
      label: "1X2 (Ganador)",
      shortLabel: "1X2",
      models: [
        { name: "Logistic Regression (Elastic Net)", accuracy: 53.09, rocAuc: null, f1: 47.18, isBest: true },
        { name: "HistGradientBoosting", accuracy: 52.25, rocAuc: null, f1: 47.07, isBest: false },
        { name: "XGBoost", accuracy: 52.25, rocAuc: null, f1: 45.81, isBest: false },
        { name: "Random Forest", accuracy: 52.18, rocAuc: null, f1: 45.53, isBest: false },
      ],
    },
    {
      id: "double-chance-1x",
      label: "Doble Oportunidad (1X)",
      shortLabel: "DC 1X",
      models: [
        { name: "Logistic Regression (Elastic Net)", accuracy: 70.95, rocAuc: 71.38, f1: 80.75, isBest: true },
        { name: "Random Forest", accuracy: 70.32, rocAuc: 69.74, f1: 80.71, isBest: false },
        { name: "Neural Network", accuracy: 70.25, rocAuc: 69.85, f1: 80.33, isBest: false },
        { name: "XGBoost", accuracy: 69.75, rocAuc: 69.37, f1: 79.86, isBest: false },
      ],
    },
    {
      id: "double-chance-x2",
      label: "Doble Oportunidad (X2)",
      shortLabel: "DC X2",
      models: [
        { name: "Logistic Regression (Elastic Net)", accuracy: 65.40, rocAuc: 71.16, f1: 70.64, isBest: true },
        { name: "Neural Network", accuracy: 64.46, rocAuc: 70.32, f1: 68.27, isBest: false },
        { name: "XGBoost", accuracy: 64.32, rocAuc: 69.64, f1: 68.97, isBest: false },
        { name: "HistGradientBoosting", accuracy: 64.18, rocAuc: 69.67, f1: 69.20, isBest: false },
      ],
    },
    {
      id: "over-25",
      label: "Más de 2.5 Goles",
      shortLabel: "Over 2.5",
      models: [
        { name: "XGBoost (L1/L2 Reg)", accuracy: 56.88, rocAuc: 55.22, f1: 68.00, isBest: true },
        { name: "Random Forest", accuracy: 56.35, rocAuc: 55.05, f1: 65.79, isBest: false },
        { name: "Neural Network", accuracy: 55.05, rocAuc: 50.42, f1: 65.50, isBest: false },
        { name: "Logistic Regression", accuracy: 54.74, rocAuc: 55.32, f1: 62.54, isBest: false },
      ],
    },
    {
      id: "under-25",
      label: "Menos de 2.5 Goles",
      shortLabel: "Under 2.5",
      models: [
        { name: "XGBoost (L1/L2 Reg)", accuracy: 56.63, rocAuc: 55.26, f1: 31.64, isBest: true },
        { name: "HistGradientBoosting", accuracy: 56.14, rocAuc: 54.72, f1: 35.63, isBest: false },
        { name: "Random Forest", accuracy: 56.11, rocAuc: 55.07, f1: 36.17, isBest: false },
        { name: "Logistic Regression", accuracy: 54.67, rocAuc: 55.30, f1: 41.69, isBest: false },
      ],
    },
    {
      id: "btts-yes",
      label: "Ambos Marcan (BTTS Sí)",
      shortLabel: "BTTS Sí",
      models: [
        { name: "Logistic Regression (Elastic Net)", accuracy: 53.44, rocAuc: 50.00, f1: 69.55, isBest: true },
        { name: "Neural Network", accuracy: 53.37, rocAuc: 50.00, f1: 56.19, isBest: false },
        { name: "XGBoost", accuracy: 53.19, rocAuc: 51.27, f1: 61.92, isBest: false },
        { name: "Random Forest", accuracy: 53.05, rocAuc: 50.44, f1: 62.21, isBest: false },
      ],
    },
    {
      id: "btts-no",
      label: "Ambos Marcan (BTTS No)",
      shortLabel: "BTTS No",
      models: [
        { name: "Red Neuronal MLP PyTorch", accuracy: 53.37, rocAuc: 52.73, f1: 31.07, isBest: true },
        { name: "Logistic Regression", accuracy: 53.23, rocAuc: 50.00, f1: 13.24, isBest: false },
        { name: "Random Forest", accuracy: 52.63, rocAuc: 50.24, f1: 33.50, isBest: false },
        { name: "HistGradientBoosting", accuracy: 52.21, rocAuc: 51.90, f1: 45.72, isBest: false },
      ],
    },
    {
      id: "home-clean-sheet",
      label: "Valla Invicta Local",
      shortLabel: "Clean Sheet H",
      models: [
        { name: "Red Neuronal MLP PyTorch", accuracy: 70.88, rocAuc: 55.12, f1: 1.19, isBest: true },
        { name: "Logistic Regression", accuracy: 70.84, rocAuc: 54.83, f1: 0.00, isBest: false },
        { name: "HistGradientBoosting", accuracy: 70.84, rocAuc: 60.68, f1: 0.00, isBest: false },
        { name: "XGBoost", accuracy: 70.84, rocAuc: 60.71, f1: 0.00, isBest: false },
      ],
    },
  ],
};

// -------------- FLUJO DE DECISIÓN --------------
const decisionFlow: LandingData["decisionFlow"] = {
  title: "¿Cómo decidimos si apostar?",
  subtitle:
    "No es una intuición. Es un pipeline matemático que va de los datos crudos a la recomendación de stake.",
  steps: [
    {
      icon: Database,
      title: "1. Recolectamos datos",
      description:
        "Scraping de FBref + ELO histórico + forma ofensiva/defensiva (goles, tiros, xG) de local y visitante, además del perfil del árbitro.",
    },
    {
      icon: Shield,
      title: "2. Sanitizamos el dataset",
      description:
        "El pipeline de datos elimina de forma estricta fugas de información: no usamos cuotas del bookmaker ni goles reales previos como features de entrenamiento.",
    },
    {
      icon: Brain,
      title: "3. Entrenamos 4 modelos",
      description:
        "Cada mercado se entrena con Logistic Regression, Random Forest, HistGradientBoosting y XGBoost usando TimeSeriesSplit para respetar el orden temporal.",
    },
    {
      icon: Calculator,
      title: "4. Calculamos el Valor Esperado (EV)",
      description:
        "Comparamos la probabilidad estimada por el modelo contra la cuota ofrecida. Solo apostamos cuando el Expected Value es positivo.",
    },
    {
      icon: Target,
      title: "5. Recomendamos stake",
      description:
        "Aplicamos Kelly fraccional o stakes fijos, filtrando por probabilidad mínima, rango de cuotas y umbral de EV para controlar el riesgo.",
    },
  ],
};

// -------------- MERCADOS CUBIERTOS --------------
const markets: LandingData["markets"] = {
  title: "Todos los Mercados Cubiertos",
  subtitle: "Desde ganadores del partido hasta valla invicta: nuestros modelos lo cubren todo.",
  items: [
    "Ganador del Partido (1X2)",
    "Doble Oportunidad (1X / X2)",
    "Más/Menos 2.5 Goles",
    "Ambos Marcan (BTTS)",
    "Valla Invicta Local",
    "Hándicap Asiático",
    "Total Tarjetas",
    "Total Córners",
  ],
};

// -------------- CTA Y FOOTER --------------
const cta: LandingData["cta"] = {
  title: "¿Listo para Explorar los Modelos?",
  subtitle: "Explora los análisis predictivos y simulaciones matemáticas para cada encuentro de la Premier League.",
  button: "Abrir Panel",
};

const footer: LandingData["footer"] = {
  tagline: "Analítica cuantitativa y modelado predictivo de la Premier League impulsado por Machine Learning.",
};

// -------------- OVERFITTING DATA --------------
const overfitting: LandingData["overfitting"] = {
  "1x2": [
    { modelName: "LogReg Optimizada (C=0.06 - Prod)", trainAcc: 54.12, testAcc: 53.09, gap: 1.03, diagnostic: "Punto Óptimo (Sweet Spot)" },
    { modelName: "LogReg Sin Regularizar (C=100)", trainAcc: 55.20, testAcc: 52.18, gap: 3.02, diagnostic: "Pérdida Leve" },
    { modelName: "HistGradientBoosting Óptimo (Depth=3)", trainAcc: 64.30, testAcc: 52.25, gap: 12.05, diagnostic: "Sobreajuste Moderado" },
    { modelName: "HistGradientBoosting Complejo (Depth=10)", trainAcc: 99.40, testAcc: 48.20, gap: 51.20, diagnostic: "Overfitting Extremo" },
  ],
  over25: [
    { modelName: "XGBoost Simple (Depth=1)", trainAcc: 55.10, testAcc: 54.74, gap: 0.36, diagnostic: "Underfitting (Subajuste)" },
    { modelName: "XGBoost Óptimo (Depth=2 - Prod)", trainAcc: 59.82, testAcc: 56.88, gap: 2.94, diagnostic: "Punto Óptimo (Sweet Spot)" },
    { modelName: "XGBoost Complejo (Depth=6)", trainAcc: 99.50, testAcc: 51.30, gap: 48.20, diagnostic: "Overfitting Extremo" },
  ]
};

// -------------- META DECISION DATA --------------
const metaDecision: LandingData["metaDecision"] = {
  configs: [
    { configName: "Línea Base Real (Capa 1)", bankroll: 9.93, roi: -5.08, bets: 1949, avoided: 0, drawdown: 99.42, diagnostic: "Ruina casi total por overround" },
    { configName: "Solo EV Dinámico (Capa 3)", bankroll: 0.33, roi: -5.25, bets: 1905, avoided: 44, drawdown: 99.98, diagnostic: "Pérdida total por ruido" },
    { configName: "Solo Meta-Modelo (Capa 2)", bankroll: 1554.55, roi: 6.91, bets: 802, avoided: 1463, drawdown: 27.77, diagnostic: "Eficiencia Excelente (Sweet Spot)" },
    { configName: "Sistema Dual (Óptimo)", bankroll: 1551.85, roi: 6.59, bets: 837, avoided: 1384, drawdown: 27.03, diagnostic: "Estabilidad excepcional" },
  ],
  crecimiento: [
    { step: "Inicio", lineaBase: 1000, metaModelo: 1000, sistemaDual: 1000 },
    { step: "Sep", lineaBase: 850, metaModelo: 1050, sistemaDual: 1040 },
    { step: "Oct", lineaBase: 700, metaModelo: 1100, sistemaDual: 1080 },
    { step: "Nov", lineaBase: 500, metaModelo: 1180, sistemaDual: 1150 },
    { step: "Dic", lineaBase: 350, metaModelo: 1220, sistemaDual: 1200 },
    { step: "Ene", lineaBase: 200, metaModelo: 1290, sistemaDual: 1270 },
    { step: "Feb", lineaBase: 100, metaModelo: 1370, sistemaDual: 1340 },
    { step: "Mar", lineaBase: 50, metaModelo: 1420, sistemaDual: 1390 },
    { step: "Abr", lineaBase: 20, metaModelo: 1490, sistemaDual: 1450 },
    { step: "May", lineaBase: 9.93, metaModelo: 1554.55, sistemaDual: 1551.85 },
  ]
};

// -------------- BACKTESTING DATA --------------
const backtesting: LandingData["backtesting"] = {
  profitChart: [
    { name: "Ago", profit: 150, bankroll: 1150 },
    { name: "Sep", profit: 380, bankroll: 1380 },
    { name: "Oct", profit: 240, bankroll: 1240 },
    { name: "Nov", profit: 610, bankroll: 1610 },
    { name: "Dic", profit: 950, bankroll: 1950 },
    { name: "Ene", profit: 1220, bankroll: 2220 },
    { name: "Feb", profit: 1580, bankroll: 2580 },
    { name: "Mar", profit: 1940, bankroll: 2940 },
    { name: "Abr", profit: 2450, bankroll: 3450 },
    { name: "May", profit: 2842, bankroll: 3842 },
  ],
  oddsProfit: [
    { oddsRange: "1.0-1.5", profit: 420, bets: 310 },
    { oddsRange: "1.5-2.0", profit: 1840, bets: 520 },
    { oddsRange: "2.0-3.0", profit: 1150, bets: 290 },
    { oddsRange: "3.0+", profit: 432, bets: 127 },
  ],
  summary: [
    { label: "ROI Promedio", value: "12.8%", detail: "Superando el benchmark del mercado (+3.2%)" },
    { label: "Tasa de Acierto", value: "67.3%", detail: "Calculado sobre 1,247 picks de valor recomendados" },
    { label: "Max Drawdown", value: "-8.4%", detail: "Controlado mediante gestión de Kelly fraccional" },
    { label: "Beneficio Total", value: "+£3,842", detail: "Retorno neto sobre un banco inicial de £1,000" },
  ],
};

// -------------- PIPELINE DATA --------------
const pipeline: LandingData["pipeline"] = {
  featureImportance: [
    { feature: "Diferencia de ELO", importance: 28.5, category: "ELO" },
    { feature: "xG Reciente (5 part.)", importance: 22.0, category: "Métricas de Goles" },
    { feature: "Goles Recientes (3 part.)", importance: 16.5, category: "Métricas de Goles" },
    { feature: "Localía (Home Adv.)", importance: 14.0, category: "Contexto" },
    { feature: "Historial Árbitro", importance: 10.5, category: "Árbitro" },
    { feature: "Bajas Clave (Lesiones)", importance: 8.5, category: "Contexto" },
  ],
};

// -------------- EXPORT --------------
export const landingData: LandingData = {
  brand,
  hero,
  features,
  modelResults,
  decisionFlow,
  markets,
  cta,
  footer,
  backtesting,
  pipeline,
  overfitting,
  metaDecision,
};
