
# Test diario de productividad — Streamlit

App hecha según tus instrucciones: 10 preguntas 0–3 (acepta decimales), cálculo ponderado (suma 100%), color del día + horas recomendadas y **gráfica en Matplotlib** con patrón Pomodoro (3×25’ + descansos 5/5/30) y fatiga acumulada.

## Requisitos
```bash
pip install streamlit matplotlib numpy
```

## Cómo ejecutar
```bash
streamlit run app.py
```

## Qué hace
1. Pregunta **una a una** las 10 cuestiones del test, mostrando para cada una las **explicaciones exactas 0–3**.
2. Calcula tu **% ponderado** (redondeo 1 decimal, límite [0,100]).
3. Asigna **color y horas recomendadas**:
   - Verde (≥85%): 5–6 h netas
   - Amarillo (70–84.9%): 3–4 h netas
   - Naranja (50–69.9%): 2–3 h netas
   - Rojo (<50%): 1–2 h o descanso
4. Genera **gráfica Matplotlib** siguiendo tu modelo:
   - Techo = % inicial – pendiente·t (por defecto 5 puntos/h).
   - Dentro de cada pomodoro hay una “joroba” (subes rápido y declinas suave).
   - Descansos: 40% del techo en cortos y 20% en largos (ajustables).
   - Línea umbral al 50%.
5. Permite **ajustar parámetros** en la barra lateral y **descargar la gráfica** (PNG).
6. Guarda **historial** en sesión y permite descargarlo (JSON).

## Notas
- Acepta **decimales** en cada pregunta (p. ej. 2.5).
- Puedes ajustar: horas representadas, pendiente de fatiga, duración de bloques y descansos, niveles de descansos.
- El patrón 3×25 + 5/5/30 se **repite** durante toda la ventana de horas representada.
