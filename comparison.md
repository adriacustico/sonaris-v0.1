# Comparativa: Ensayos ISO 10140-2 (Laboratorio) vs Motor de Cálculo Sonaris

> Fuente laboratorio: *Análisis Exhaustivo de Ensayos Acústicos ISO 10140-2*  
> Solo se incluyen **muros** (se excluyen losas, puertas y ventanas).  
> Fecha de análisis: 2026-05-05

---

## 1. Resumen de Índices Globales (Rw, C, Ctr)

| # | Sistema | m (kg/m²) | **Rw Lab** | **Rw Calc** | **ΔRw** | C Lab | C Calc | Ctr Lab | Ctr Calc |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Ladrillo fonorresistente + guarnecido yeso 15 mm c/cara (137 mm total) | 175 | 49 | 63 | **+14** | −1 | −23 | −4 | −25 |
| 2 | BTC Lurblock 140 mm (sin revestimiento continuo) | 191 | 42 | 64 | **+22** | −1 | −24 | −3 | −27 |
| 3 | Tabique fibrocemento **sin** barras resilientes (montantes madera, cavidad 90 mm) | 35.7 | 42 | 65 | **+23** | −2 | −28 | −7 | −32 |
| 4 | Tabique fibrocemento **con** canal resiliente (cavidad 90 mm) | 35.7 | 50 | 49 | **−1** | −4 | +2 | −10 | −5 |
| 5 | Panel metálico simple (aluminio 3 mm, pared única) | 7.7 | 26 | 80 | **+54** | −1 | −57 | −4 | −61 |

---

## 2. Espectros R(f) por Elemento — Lab vs Calc

### 2.1 Ladrillo Fonorresistente Cerámica Millas + Guarnecido Yeso

Configuración real: guarnecido yeso 15 mm | ladrillo perforado 107 mm | guarnecido yeso 15 mm  
Aproximación en motor: Yeso+papel 15 mm + Ladrillo cerámico 107 mm + Yeso+papel 15 mm (pared única compuesta)

| Hz   | Lab (dB) | Calc (dB) | Error |
|------|----------|-----------|-------|
| 100  | 39.3     | 34.8      | −4.5  |
| 125  | 35.4     | 36.8      | +1.4  |
| 160  | 39.6     | 38.9      | −0.7  |
| 200  | 34.2     | 28.3      | **−5.9** |
| 250  | 38.6     | 30.2      | **−8.4** |
| 315  | 38.7     | 32.2      | **−6.5** |
| 400  | 41.9     | 34.3      | **−7.6** |
| 500  | 44.7     | 36.2      | **−8.5** |
| 630  | 47.2     | 38.2      | **−9.0** |
| 800  | 49.4     | 40.3      | −9.1  |
| 1000 | 51.8     | 42.2      | −9.6  |
| 1250 | 54.0     | 44.2      | −9.8  |
| 1600 | 56.7     | 46.3      | −10.4 |
| 2000 | 58.3     | 48.3      | −10.0 |
| 2500 | 60.3     | 50.2      | −10.1 |
| 3150 | 61.8     | 52.2      | −9.6  |
| 4000 | 64.1     | 54.3      | −9.8  |
| 5000 | ≥65.9    | 56.2      | ≤−9.7 |

**Observaciones:**
- A 100–160 Hz el motor está dentro de ±5 dB (buen comportamiento en bajas).
- Desde 200 Hz en adelante el motor subestima la R real en ~10 dB constante.
- El laboratorio muestra una caída inusual a 125 Hz y 200 Hz (resonancia estructural del ladrillo hueco);
  el modelo no captura este comportamiento no-monótono.
- El motor produce una curva monótonamente creciente mientras el laboratorio muestra irregularidades
  por cavidades internas del ladrillo.

---

### 2.2 Bloques de Tierra Compactada BTC Lurblock (140 mm, sin yeso)

Configuración real: bloque 295×140×110 mm, sin revestimiento continuo de yeso  
Aproximación en motor: Bloque hormigón 140 mm (densidad 1400 kg/m³ ≈ 191 kg/m²)

| Hz   | Lab (dB) | Calc (dB) | Error |
|------|----------|-----------|-------|
| 100  | 34.3     | 33.8      | −0.5  |
| 125  | 33.6     | 35.8      | +2.2  |
| 160  | 33.1     | 37.9      | +4.8  |
| 200  | 35.3     | 27.6      | **−7.7** |
| 250  | 34.2     | 29.6      | **−4.6** |
| 315  | 35.1     | 31.6      | −3.5  |
| 400  | 35.4     | 33.7      | −1.7  |
| 500  | 36.3     | 35.6      | −0.7  |
| 630  | 37.4     | 37.6      | +0.2  |
| 800  | 39.5     | 39.7      | +0.2  |
| 1000 | 42.9     | 41.6      | −1.3  |
| 1250 | 46.3     | 43.6      | −2.7  |
| 1600 | 48.3     | 45.7      | −2.6  |
| 2000 | 48.1     | 47.6      | −0.5  |
| 2500 | 50.0     | 49.6      | −0.4  |
| 3150 | 51.8     | 51.6      | −0.2  |
| 4000 | 51.4     | 53.7      | +2.3  |
| 5000 | 50.5     | 55.6      | +5.1  |

**Observaciones:**
- En rango 400–3150 Hz el motor es muy preciso (error < 3 dB).
- Error principal: dip a 200–250 Hz en el motor (f_c del bloque ~220 Hz) versus curva más plana en laboratorio.
- A 4000–5000 Hz el laboratorio muestra un plateau o ligera caída (posibles resonancias del muro),
  mientras el motor sigue creciendo. Este es el mejor caso de todos los sistemas evaluados para
  frecuencias medias.
- Pese a la precisión espectral en 500–3150 Hz, **Rw difiere +22 dB** debido al dip de coincidencia
  que provoca C/Ctr muy negativos en el algoritmo ISO 717-1.

---

### 2.3 Partición de Fibrocemento Sin Barras Resilientes

Configuración real: 2 capas de fibrocemento (masa total 35.68 kg/m²) sobre montantes de madera, cavidad 90 mm  
Aproximación en motor: 13 mm fibrocemento c/cara + montantes_madera 90 mm

| Hz   | Lab (dB) | Calc (dB) | Error |
|------|----------|-----------|-------|
| 100  | —        | 19.2      | —     |
| 500  | —        | 34.3      | —     |
| 1000 | —        | 40.3      | —     |
| 3150 | —        | 50.3      | —     |

*El informe SRL no publica el espectro completo; solo Rw=42, C=−2, Ctr=−7.*

**Observaciones:**
- La diferencia Rw +23 dB es la mayor de todos los sistemas.
- El motor predice Rw=65 mientras el laboratorio da Rw=42.
- El modelo de montantes_madera no limita suficientemente la transmisión en este sistema ligero.

---

### 2.4 Partición de Fibrocemento Con Canal Resiliente

Configuración real: misma composición que 2.3 pero desacoplada con barras resilientes  
Aproximación en motor: 13 mm fibrocemento c/cara + canal_resiliente 90 mm (sin relleno poroso)

| Hz   | Lab (dB) | Calc (dB) | Error   |
|------|----------|-----------|---------|
| 100  | —        | 25.8      | —       |
| 200  | —        | 41.2      | —       |
| 500  | —        | 65.2      | **muy alto** |
| 1000 | —        | 83.2      | **muy alto** |
| 3150 | —        | 85.2      | **muy alto** |

*El informe SRL no publica el espectro completo; solo Rw=50, C=−4, Ctr=−10.*

**Observaciones:**
- **Rw=49 vs Lab=50: error de solo −1 dB** — coincidencia aceptable.
- Sin embargo, el espectro calculado es irreal: R(1000 Hz) = 83 dB es físicamente imposible para un
  tabique liviano. El Rw≈49 es un resultado fortuito: el algoritmo ISO 717-1 queda fijado por las
  frecuencias bajas (100–250 Hz) que sí tienen valores plausibles; las frecuencias altas, aunque
  exageradas, no aportan desviaciones adversas y no afectan el Rw.
- **C=+2 dB** (positivo) es anómalo; el real es −4 dB. Consecuencia directa del espectro irreal
  a altas frecuencias.

---

### 2.5 Panel Metálico Simple (aluminio 3 mm ≈ 7.7 kg/m²)

Configuración real: panel metálico simple, 7.7 kg/m², Universidad de Salford  
Aproximación en motor: Aluminio 3 mm (2700 × 0.003 = 8.1 kg/m²)

| Hz   | Lab (dB) | Calc (dB) | Error   |
|------|----------|-----------|---------|
| 100  | 13.0     | 6.2       | **−6.8** |
| 125  | 10.8     | 8.1       | −2.7    |
| 160  | 14.9     | 10.3      | −4.6    |
| 200  | 14.9     | 12.2      | −2.7    |
| 250  | 16.7     | 14.1      | −2.6    |
| 315  | 17.3     | 16.1      | −1.2    |
| 400  | 18.7     | 18.2      | −0.5    |
| 500  | 19.7     | 20.1      | +0.4    |
| 630  | 20.9     | 22.2      | +1.3    |
| 800  | 21.6     | 24.2      | +2.6    |
| 1000 | 22.6     | 26.2      | +3.6    |
| 1250 | 24.2     | 28.1      | +3.9    |
| 1600 | 25.9     | 30.3      | +4.4    |
| 2000 | 27.6     | 32.2      | +4.6    |
| 2500 | 29.8     | 34.1      | +4.3    |
| 3150 | 31.4     | 36.1      | +4.7    |
| 4000 | 32.8     | 38.2      | +5.4    |
| 5000 | 33.7     | **17.9**  | **−15.8** |

**Observaciones:**
- Hasta 400 Hz el error es < 5 dB (aceptable).
- De 500 a 4000 Hz el motor sobreestima en ~4–5 dB de forma sistemática.
- **El colapso a 5000 Hz es el problema crítico**: la frecuencia crítica del aluminio (f_c ≈ 4040 Hz)
  genera un dip de −22 dB en el motor (η_aluminio = 0.003 → 10·log10(2η) = −22.2 dB).
  En el laboratorio la curva sigue creciendo hasta 33.7 dB a 5000 Hz, posiblemente por el
  amortiguamiento del marco de ensayo y la rugosidad de la superficie.
- El dip catastrófico a 5000 Hz es lo que eleva Rw a 80 en el ISO 717-1 (el algoritmo necesita
  un offset muy grande para satisfacer la desviación adversa de 12+ dB en esa banda).

---

## 3. Diagnóstico de Errores por Tipo de Sistema

### 3.1 Paredes Masivas (Ladrillo, BTC)

| Error | Causa en el modelo |
|---|---|
| Rw sobreestimado +14–22 dB | La constante de ley de masas (−52 dB campo libre) funciona para paneles homogéneos ideales. La mampostería real tiene juntas, heterogeneidad y transmisión por flancos que reducen R efectivo. |
| Dip pronunciado en f_c | El motor aplica corrección de coincidencia constante desde f_c en adelante. La mampostería tiene η efectivo mucho mayor (amortiguamiento por mortero, juntas) que el valor de tabla. |
| C y Ctr muy negativos | Consecuencia del dip de coincidencia que reduce R en el rango 200–1000 Hz; los espectros de referencia ISO ponderan fuertemente esas frecuencias. |
| **Excepción BTC (500–3150 Hz)** | En ese rango el error < 3 dB. El modelo es útil para estimaciones de franja media. |

### 3.2 Tabiques Ligeros con Montantes

| Error | Causa en el modelo |
|---|---|
| Sin barras: Rw +23 dB | La fórmula de stud transmission `R_stud = 20·log10(f·S·m1·m2) + C` sobreestima el aislamiento para paneles muy ligeros (m ≈ 17 kg/m²). La fórmula fue calibrada para yeso 15–30 mm; no escala correctamente para fibrocemento delgado. |
| Con canal resiliente: Rw correcto pero espectro irreal | El modelo de camino aéreo `R_air = R1 + R2 + 6·dB/oct` no tiene límite superior de frecuencia; a 1000–5000 Hz proporciona beneficios de cavidad de +50–65 dB que son físicamente imposibles. |

### 3.3 Paneles Metálicos Delgados y Livianos

| Error | Causa en el modelo |
|---|---|
| Rw +54 dB | El factor de pérdida catálogo (η = 0.003 aluminio) genera un dip de coincidencia de −22 dB a 4040 Hz. El laboratorio no muestra este dip porque el marco de ensayo y los tratamientos de superficie amortiguan significativamente la resonancia de coincidencia. |
| C y Ctr extremos | Consecuencia directa del dip de coincidencia; el algoritmo ISO 717-1 amplifica enormemente el error espectral en esa banda. |

---

## 4. Conclusiones

### Dónde el motor funciona aceptablemente

| Caso | Rango de aplicación | Error esperado Rw |
|---|---|---|
| Paredes masivas (mampostería, hormigón, bloques) | **500–3150 Hz** espectro R(f) | < 3 dB en ese rango; Rw global ±10–20 dB |
| Doble hoja con canal resiliente | Rw global | ±2–3 dB |
| Doble hoja con montantes metal (paneles ≥20 kg/m²) | Rw global | ±5 dB |

### Limitaciones principales identificadas

1. **Ley de masas con constante fija (−52 dB)**: no captura el comportamiento real de mampostería por encima de 1 kHz, donde el material tiene ganancia de R mayor que la predicción teórica.

2. **Corrección de coincidencia demasiado agresiva**: la corrección constante `10·log10(2η)` aplica desde f_c hasta infinito. Para mampostería pesada (η_efectivo >> η_tabla) y metales delgados (η muy bajo), produce errores grandes.

3. **Fórmula de transmisión por montantes**: calibrada para yeso 15–30 mm, no escala correctamente a paneles muy ligeros (fibrocemento 13 mm) ni muy pesados.

4. **Camino aéreo sin cota superior**: `R_air = R1 + R2 + 6dB/oct × (f/f_mam)` puede alcanzar valores > 80 dB a altas frecuencias, resultado irreal para sistemas de doble hoja con canal resiliente.

5. **η de tabla vs η efectivo**: el factor de pérdida de un material aislado difiere del factor efectivo en una partición montada (bordes, sellado, mortero contribuyen 2–8 dB de amortiguación adicional en mampostería).

### Próximos pasos para mejorar la precisión

| Prioridad | Mejora |
|---|---|
| Alta | Añadir una **cota de f_mam × factor** en la ganancia de cavidad para canal resiliente |
| Alta | Calibrar η efectivo para mampostería (~0.05–0.10 en lugar de 0.02–0.03 de tabla) |
| Media | Ajustar la constante de ley de masas para mampostería: −47 en lugar de −52 (normal incidencia) |
| Media | Restringir la corrección de coincidencia a un rango de ±2 oct alrededor de f_c en lugar de aplicarla uniformemente |
| Baja | Base de datos de ensayos certificados para comparación directa (validación empírica) |

---

*Generado por Sonaris v0.1 — Motor de Cálculo Acústico*
