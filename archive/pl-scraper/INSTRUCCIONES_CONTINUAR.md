# Instrucciones para Continuar el Scraping

Este documento describe el estado exacto en el que se detuvo el scraper y los pasos necesarios para reanudar el trabajo desde otro equipo. El objetivo es que todas las temporadas (2017 a 2024, incluyendo 21/22) queden exactamente iguales, es decir, con las extracciones de **Alineaciones (Lineups)**, **Eventos (Events)**, **Tiros (Shots)** y las **6 Estadísticas de Jugadores (Player Stats)** completadas.

---

## 🛑 1. Estado Actual (Marzo 2026)

Se avanzó significativamente. Las temporadas más pesadas ya descargaron todos sus datos partido a partido. Aquí está el progreso exacto:

| Temporada | Alineaciones | Eventos | Tiros (Shots) | Stats Jug. | Capacidad para MÁS datos (Advanced Stats) |
|-----------|--------------|---------|----------------|------------|-----------------------------------------|
| **2024** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Alta**: FBref tiene data extensa (Passing/Defense) actual |
| **2023** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Alta**: FBref tiene data extensa (Passing/Defense) actual |
| **2022** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Alta**: FBref tiene data extensa (Passing/Defense) actual |
| **21/22** | 380/380 | 380/380 | 🚫 Inexistente | 0 de 6 | **Alta**: Faltan stats básicos pero FBref los provee |
| **2020** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Media**: Empieza a haber registro Opta/StatsBomb |
| **2019** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Media**: Empieza a haber registro Opta/StatsBomb |
| **2018** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Baja**: Primer año con ciertas métricas faltantes |
| **2017** | 380/380 | 380/380 | 🚫 Inexistente | 2 de 6 | **Baja**: FBref histórico tiene registros muy limitados |

### 🛠 Consideraciones sobre el Estado Real y Verificado:
1. **Métricas Faltantes (`shot_events.csv`, 4 de 6 stats):** La tabla anterior (2025/2026) reportaba erróneamente que había descargas pendientes de tiros. En realidad FBref impidió/bloqueó el acceso a través de las APIs actuales de la librería, provocando descargas de tablas vacías. Todos los tiros han sido ignorados exitosamente para no colapsar / ensuciar el simulador.
2. **Obtención de Más Datos:** Solo disponemos de los resúmenes genéricos de los jugadores y arqueros. Para las temporadas desde 2021 a 2024 es **altamente posible** mejorar el scrapeo extrayendo datos avanzados (Defensa, Posesión, Pases), ya que constan de registros óptimos por Opta; no obstante, las de 2017 y 2018 poseen muchas de éstas carentes.

---

## 🚀 2. Cómo Continuar en el Nuevo Equipo

Todo el sistema de estados está sincronizado. Al llevarte este repositorio al nuevo equipo, el scraper sabrá **exactamente** dónde retomar gracias a los archivos `checkpoint_<season>.json`.

**Pasos a seguir:**

1. Clona/actualiza el repositorio en el nuevo equipo.
2. Activa el entorno virtual e instala dependencias:
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Ejecuta el script automatizado (puedes dejarlo corriendo de fondo usando `nohup` o en una sesión de `tmux`):
   ```bash
   python run_all_seasons.py
   ```

El script revisará automáticamente el orden de prioridades, detectará que 21/22, 2024, etc., ya no necesitan descargas de partidos, e irá directamente a continuar descargando los **tiros de 2018**.

*Nota: Para monitorear el progreso mientras corre en el otro equipo, puedes ejecutar en otra terminal `python status.py`.*
