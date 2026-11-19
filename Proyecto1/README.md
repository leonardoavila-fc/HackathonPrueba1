# 🏈 NFL Coach Analytics: Decisiones Tácticas Basadas en Datos

Esta plataforma procesa más de 411,000 jugadas históricas de la NFL (2002-2012) para validar heurísticas de entrenamiento y descubrir ineficiencias tácticas mediante análisis de datos. 

## 📊 Hallazgos Principales (Demo)

1. **El Espejismo del *No Huddle* en el 4to Cuarto**
   * **El Mito:** Acelerar la ofensiva sin reunión en el Q4 genera una ventaja estadística (+0.76 yds por jugada).
   * **La Realidad (Partidos Cerrados):** Al aislar el *garbage time* y analizar únicamente partidos con diferencia de ≤ 8 puntos, la ventaja desaparece. El *No Huddle* pierde **-0.51 yardas netas** y eleva el riesgo de *turnover* de 3.5% a **4.4%**. 
   * *Acción:* Reservar el *No Huddle* estrictamente para el manejo del reloj, no como un generador de yardas en situaciones críticas.

2. **La Ventaja de la Carrera desde *Shotgun* (3ro y Medio)**
   * En situaciones de 3er down y 3-6 yardas, las defensas asumen un sesgo de pase y aligeran la caja. Correr desde una formación *Shotgun* rompe esta tendencia logrando un **54.8% de conversión** (5.98 yds), destrozando el **44.2%** (4.63 yds) de las carreras tradicionales bajo el centro (+10.6 puntos porcentuales de efectividad).

3. **Auditoría Estricta de Calidad de Datos (Métricas de Riesgo Real)**
   * **Turnovers de Pase Netos:** Se integraron `SACK` e `INTERCEPTION` dentro del volumen total de pases, evitando que el riesgo aéreo quedara subestimado y las yardas promedio infladas.
   * **Sesgo de Registro en Zonas:** Se excluyeron los más de 71,000 pases incompletos sin dirección registrada (`incomplete_no_dir` y `unknown`) antes de calcular la eficiencia térmica del campo, garantizando que recomendar atacar *Deep Middle* provenga de porcentajes matemáticamente puros.

## ⚙️ Arquitectura
* **Backend:** FastAPI, Python, Pandas, AWS Boto3, Strands Agents (IA).
* **Frontend:** React, TypeScript, Vite, TailwindCSS, Recharts.
