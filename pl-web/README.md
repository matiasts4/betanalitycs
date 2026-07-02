# Premier League Predictor — Aplicación Web (Frontend)

Interfaz web del sistema de predicción de apuestas. Construida con React + TypeScript + Vite. Conecta con el motor de predicción Python en el backend.

---

## 🚀 Inicio Rápido

### Requisitos
- Node.js 18+
- npm 9+
- **El servidor backend debe estar corriendo** (ver `../archive/pl-predictor/README.md`)

---

## ▶️ Comandos

### Levantar en desarrollo (con hot-reload)
```bash
npm run dev
```
La aplicación queda disponible en `http://localhost:8080` (o el puerto que indique Vite).

### Compilar para producción
```bash
npm run build
```
Los archivos optimizados quedan en la carpeta `dist/`.

### Vista previa del build de producción
```bash
npm run preview
```

### Verificar tipos TypeScript
```bash
npx tsc --noEmit
```

---

## 🔗 Integración con el Backend

La app web se comunica con la API Flask en:
```
http://localhost:5000/api/...
```

Para que la web funcione correctamente **debes tener el backend corriendo en paralelo**. Pasos completos:

**Terminal 1 — Backend (Python)**
```bash
cd archive/pl-predictor
python -m src.api
```

**Terminal 2 — Frontend (Node)**
```bash
cd pl-web
npm run dev
```

También puedes usar el `.bat` de conveniencia en la raíz del proyecto:
```bash
# Windows — levanta backend y frontend automáticamente
start-next-es.bat
```

---

## 🗂 Estructura de Carpetas

```
pl-web/
├── src/
│   ├── components/         # Componentes reutilizables (AppSidebar, MatchCard, etc.)
│   ├── lib/
│   │   └── api.ts          # Interfaces TypeScript + React Query hooks para todos los endpoints
│   ├── pages/
│   │   ├── Dashboard.tsx   # Página principal con próximos partidos
│   │   ├── Predictor.tsx   # Predicción manual de un partido (elige equipos + fecha)
│   │   ├── Simulator.tsx   # Simulador financiero de apuestas con Kelly Criterion
│   │   ├── Performance.tsx # Gráficas del backtest histórico y ROI
│   │   ├── DetailedHistory.tsx # Historial detallado con los 16 mercados por partido
│   │   ├── History.tsx     # Historial resumido de apuestas
│   │   └── Teams.tsx       # Rankings y estadísticas de equipos con Elo
│   ├── App.tsx             # Rutas principales de la app
│   └── index.css           # Estilos globales y sistema de diseño
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.ts
```

---

## 📄 Páginas Disponibles

| Ruta                  | Descripción                                                  |
|-----------------------|--------------------------------------------------------------|
| `/`                   | Dashboard — próximos partidos y predicciones del día         |
| `/predictor`          | Predice cualquier partido eligiendo equipo, fecha y variables|
| `/simulator`          | Simula tu portafolio de apuestas con parámetros configurables|
| `/performance`        | Gráficas de ROI histórico y métricas del backtester          |
| `/detailed-history`   | Historial exhaustivo: 16 mercados evaluados por partido      |
| `/history`            | Últimas apuestas registradas con resultado Real vs Predicho  |
| `/teams`              | Ranking de todos los equipos con Elo, forma y estadísticas   |

---

## ⚙️ Variables del Simulador

El Simulador (`/simulator`) soporta las siguientes configuraciones:

| Parámetro            | Descripción                                                   |
|----------------------|---------------------------------------------------------------|
| Capital Inicial      | Monto de partida de la simulación (ej. $100,000)              |
| Estrategia           | **Fija**: apuesta constante / **Variable (Kelly)**: proporcional a probabilidad |
| Monto de Apuesta     | Fija: monto por apuesta / Variable: % máximo del capital      |
| Cuota Mínima (EV)    | Ignora apuestas cuya cuota esperada sea menor a este umbral   |
| Filtro de Tiempo     | Simula en una temporada específica o los últimos N partidos   |
| Cantidad de Partidos | Solo aplica si el filtro de tiempo = "Últimos N partidos"     |

### 🏆 Configuración Óptima Recomendada
Basado en 432 pruebas de grid search:
- **Estrategia**: Variable (Kelly Criterion)
- **Fracción máxima**: 15% del capital por apuesta
- **Cuota Mínima**: 1.80
- **Período**: Temporada 2023/2024
- **Winrate**: 62.1% | **ROI**: +3,347%
