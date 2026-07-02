# Diccionario y Estado de los Datos (Premier League Scraper)

Este documento detalla la estructura y disponibilidad exacta de los datos extraídos para que el **simulador** pueda consumir la información de manera correcta y evitar errores por archivos faltantes o columnas inconsistentes.

## Resumen de Temporadas Extraídas
Actualmente el scraper ha completado la extracción de datos para las siguientes temporadas (cada una en su respectiva carpeta bajo `data/processed/<season>`):
- **2017 a 2024** completadas (la antigua "2122" fue corregida y normalizada como "2021" en el repositorio final del predictor).
- **2025** *(Temporada en curso 2025/2026)*: Actualmente en proceso de extracción. Los datos reflejarán los partidos jugados hasta la fecha actual.

> **⚠️ AVISO IMPORTANTE (Tiros / Shots)**  
> **No existe el archivo `shot_events.csv` en NINGUNA temporada.**  
> *Razón:* FBref ha bloqueado o cambiado irrevocablemente la estructura de las tablas de tiros avanzados, por lo tanto el módulo `soccerdata` retorna datos vacíos sistemáticamente. El simulador **debe ser configurado para no depender de `shot_events.csv`**.

---

## Archivos Garantizados por Temporada

Los siguientes archivos están presentes en el 100% de las carpetas de las temporadas extraídas.

### 1. `matches.csv`
Contiene la información general de calendario y resultado de los 380 partidos jugados por temporada.
- **Formato:** 380 filas × 16 columnas.
- **Uso en el simulador:** Referencia principal para buscar el `game_id` o `match_id`, la fecha, y el resultado global del partido.

### 2. `lineups.csv`
Contiene la información de los jugadores convocados (titulares y suplentes) para cada equipo en cada partido.
- **Filas:** ~13,600 filas (2017 a 2020) y ~18,000 a ~30,000 filas (2022 en adelante). 
- *Razón de la diferencia en filas:* El cambio en la regla de suplentes en el fútbol post-COVID (bancas ampliadas de 5/7 jugadores a 9 jugadores) hace que haya muchos más registros para las temporadas recientes.
- **Uso en el simulador:** Identificar qué jugadores participaron y en qué minuto entraron/salieron.

### 3. `match_events.csv`
Registro de todos los eventos minuto a minuto (goles, tarjetas, sustituciones, asistencias).
- **Filas:** Aprox. 4,000 a 11,000 filas dependiendo de la temporada.
- **Uso en el simulador:** Reconstruir cronológicamente lo sucedido en un encuentro.

### 4. `player_stats_summary.csv`
Estadísticas agregadas por cada jugador a lo largo de un partido (minutos jugados, goles anotados, pases, etc).
- **Filas:** Aprox. 10,000 a 11,500 filas por temporada.
- **Uso en el simulador:** Evaluar el rendimiento individual en métricas estándar.

### 5. `player_stats_keepers.csv`
Estadísticas exclusivas de los porteros para cada partido (tiros al arco enfrentados, atajadas, goles concedidos).
- **Filas:** Aprox. 760 a 770 filas por temporada (usualmente 2 porteros × 380 partidos).
- **Uso en el simulador:** Medir el rendimiento defensivo del arco.

---

## Inconsistencias Resueltas
- La temporada **21/22** ("2122") presentaba partidos duplicados (760 filas en `matches.csv`), lo cual generaba el doble de procesamientos o errores de duplicidad de llaves en el simulador. **Esto fue corregido**, devolviendo el número exacto a los 380 partidos únicos.
- El error que hacía que el simulador buscara `shots_done` ha de omitirse o inhabilitarse, dado que los tiros carecen de soporte oficial actualizado y por ende fueron reportados como terminados vacíos por el scraper.
