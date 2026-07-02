# Actualización de la Landing Page

Este documento explica cómo mantener actualizada la landing page de **BetAnalitycs** sin necesidad de tocar componentes React.

## Archivo fuente

Todo el contenido visible en la landing se define en:

```
pl-web/src/data/landingData.ts
```

`Landing.tsx` solo se encarga de renderizar esos datos. Si querés cambiar textos, números, resultados de modelos o el flujo de decisión, editá ese archivo.

---

## Estructura del archivo

```ts
export const landingData: LandingData = {
  brand,          // nombre, tagline, CTAs
  hero,           // headline, descripción y stats principales
  features,       // tarjetas de características
  modelResults,   // resultados de modelos por mercado
  decisionFlow,   // pasos del pipeline de decisión
  markets,        // mercados cubiertos
  cta,            // llamado a la acción final
  footer,         // pie de página
};
```

A continuación, cómo actualizar cada sección.

---

## 1. Brand, hero y CTAs

```ts
const brand = {
  name: "BetAnalitycs",
  tagline: "Apuestas más inteligentes. Mayores ventajas.",
  description: "Nuestra IA analiza miles de puntos de datos...",
  ctaPrimary: "Abrir Panel",
  ctaSecondary: "Saber más",
};
```

- `name`: nombre que aparece en el navbar y el footer.
- `tagline`: no se muestra directamente en la landing actual, pero está disponible para futuras secciones.
- `description`: texto del hero y del SEO/meta si se usa.
- `ctaPrimary` / `ctaSecondary`: textos de los botones del hero.

### Stats del hero

```ts
const heroStats: HeroStat[] = [
  { label: "Tasa de Acierto", value: "67.3%", icon: Target },
  { label: "ROI", value: "12.8%", icon: TrendingUp },
  { label: "Predicciones", value: "1,247", icon: BarChart3 },
  { label: "Beneficio Total", value: "£3,842", icon: Zap },
];
```

- `value`: string libre. Podés poner el formato que quieras (porcentajes, números con separador de miles, etc.).
- `icon`: componente de `lucide-react`. Ver disponibles en https://lucide.dev/icons.

---

## 2. Características (features)

```ts
const features: Feature[] = [
  {
    icon: BarChart3,
    title: "Análisis Profundo de Partidos",
    description: "Probabilidades de victoria...",
  },
  // ...
];
```

Cada objeto es una tarjeta. Podés agregar, quitar o reordenar libremente. Se muestran en una grilla de 3 columnas en desktop.

---

## 3. Resultados de modelos

Esta es la sección más importante para mantener actualizada. Los datos deben coincidir con la salida de:

```bash
python generate_model_results_table.py
```

Ese script genera:

- `Carpeta_Presentacion/14_Tabla_Resultados_Modelos_V8.csv`
- `Carpeta_Presentacion/14_Tabla_Resultados_Modelos_V8.png`

### Cómo actualizar

1. Correr el script de modelos:

   ```bash
   python generate_model_results_table.py
   ```

2. Abrir el CSV generado:

   ```
   Carpeta_Presentacion/14_Tabla_Resultados_Modelos_V8.csv
   ```

3. Copiar los valores de `accuracy`, `roc_auc` y `f1` al array `modelResults.markets` en `landingData.ts`.
4. Marcar `isBest: true` únicamente en el modelo con mayor `accuracy` de cada mercado.

### Formato esperado

```ts
{
  id: "1x2",
  label: "1X2 (Ganador)",
  shortLabel: "1X2",
  models: [
    { name: "Random Forest", accuracy: 53.12, rocAuc: null, f1: 46.39, isBest: true },
    { name: "Logistic Regression", accuracy: 52.30, rocAuc: null, f1: 46.93, isBest: false },
    // ...
  ],
}
```

- `id`: clave única, sin espacios.
- `label`: título largo que aparece dentro de la pestaña.
- `shortLabel`: texto de la pestaña.
- `rocAuc`: `null` cuando no aplica (por ejemplo, en 1X2 multiclase).

### Nota sobre la fuente

El texto `modelResults.source` debe reflejar el dataset y la metodología. Actualizalo si cambia la versión del pipeline (por ejemplo, de V8 a V9).

---

## 4. Flujo de decisión

```ts
const decisionFlow = {
  title: "¿Cómo decidimos si apostar?",
  subtitle: "...",
  steps: [
    {
      icon: Database,
      title: "1. Recolectamos datos",
      description: "...",
    },
    // ...
  ],
};
```

Cada paso es un item del timeline. Podés agregar o quitar pasos; el conector se adapta visualmente.

---

## 5. Mercados cubiertos

```ts
const markets = {
  title: "Todos los Mercados Cubiertos",
  subtitle: "...",
  items: [
    "Ganador del Partido (1X2)",
    // ...
  ],
};
```

La lista `items` genera las tarjetas de mercados. Agregá o quitá según los mercados que entrenes.

---

## 6. CTA y footer

```ts
const cta = {
  title: "¿Listo para Encontrar tu Ventaja?",
  subtitle: "Comienza a explorar predicciones...",
  button: "Abrir Panel",
};

const footer = {
  tagline: "Analíticas de apuestas de la Premier League...",
};
```

---

## Convenciones

- **Íconos:** todos vienen de `lucide-react`. Importalos desde el mismo paquete y usalos como componente (`icon: Target`).
- **Colores:** no hardcodees colores en este archivo. Los estilos vienen de `index.css` y `tailwind.config.ts`.
- **Tipos:** el archivo exporta las interfaces `HeroStat`, `Feature`, `ModelResult`, `MarketResult`, `DecisionStep` y `LandingData`. Si cambiás la estructura, actualizá también las interfaces.

---

## Verificación

Después de editar `landingData.ts`, corré el build para asegurarte de que no hay errores:

```bash
cd pl-web
bun run build
```

o, si usás npm:

```bash
cd pl-web
npm run build
```

---

## Resumen rápido

| Querés cambiar... | Editá... |
|---|---|
| Nombre, tagline, CTAs | `brand` |
| Stats del hero | `heroStats` |
| Tarjetas de features | `features` |
| Tabla de modelos | `modelResults` (y regenerá el CSV) |
| Timeline de decisión | `decisionFlow` |
| Mercados mostrados | `markets.items` |
| CTA final / footer | `cta` / `footer` |
