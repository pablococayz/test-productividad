
# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

st.set_page_config(page_title="Test diario de productividad", page_icon="✅", layout="centered")

# ---------------------------
# Parámetros por defecto (ajustables en la barra lateral)
# ---------------------------
with st.sidebar:
    st.header("Parámetros del modelo")
    horas_totales = st.number_input("Horas representadas", min_value=2.0, max_value=12.0, value=8.0, step=0.5, help="Longitud del día en la gráfica")
    pendiente_fatiga = st.number_input("Pendiente de fatiga (puntos/hora)", min_value=0.0, max_value=15.0, value=5.0, step=0.5, help="Cuánto desciende el 'techo' por hora")
    dur_pomo = st.number_input("Duración Pomodoro (min)", min_value=15, max_value=60, value=25, step=5)
    descanso_corto = st.number_input("Descanso corto (min)", min_value=3, max_value=15, value=5, step=1)
    descanso_largo = st.number_input("Descanso largo (min)", min_value=10, max_value=60, value=30, step=5)
    suelo_descanso_corto = st.number_input("Nivel en descanso corto (×techo)", min_value=0.0, max_value=1.0, value=0.40, step=0.05)
    suelo_descanso_largo = st.number_input("Nivel en descanso largo (×techo)", min_value=0.0, max_value=1.0, value=0.20, step=0.05)

st.title("🧠 Test diario de productividad")
st.caption("App creada según tus especificaciones: test 0–3 (con decimales), cálculo ponderado, color + horas recomendadas y gráfica Matplotlib acorde al patrón 3×25’ + descansos.")

# ---------------------------
# Definición del test (exactamente como en tu documento)
# ---------------------------

ITEMS = [
    {
        "key": "sueno",
        "titulo": "1. Sueño (20%)",
        "peso": 20.0,
        "pregunta": "¿Cómo dormiste anoche en **calidad y cantidad**?",
        "explicaciones": {
            0: "Dormí fatal (<5h, sueño interrumpido). ➝ Muy mal descanso, memoria y atención casi bloqueadas. Jornada muy limitada.",
            1: "Dormí poco (5–6h). ➝ Arrancas cansado, atención corta. 2–3h útiles como máximo.",
            2: "Dormí normal (6–7h). ➝ Rindes aceptablemente, aunque no al máximo. Nivel “amarillo”.",
            3: "Dormí bien (7–9h, reparador). ➝ Alta energía, memoria y concentración. Día ideal para 5–6h efectivas."
        }
    },
    {
        "key": "energia",
        "titulo": "2. Energía corporal (10%)",
        "peso": 10.0,
        "pregunta": "¿Cómo notas tu nivel físico ahora mismo?",
        "explicaciones": {
            0: "Agotado físicamente. ➝ Incluso tareas simples cuestan, no podrías mantenerte sentado mucho tiempo.",
            1: "Energía baja. ➝ Te arrastras un poco, estudiar será más pesado de lo normal.",
            2: "Energía aceptable. ➝ Puedes aguantar varios bloques, aunque sentirás fatiga antes.",
            3: "Energía alta. ➝ Te sientes fuerte y descansado, con vitalidad para toda la jornada."
        }
    },
    {
        "key": "dolor",
        "titulo": "3. Dolores o molestias físicas (2,5%)",
        "peso": 2.5,
        "pregunta": "¿Tienes algún dolor que pueda distraerte hoy (cabeza, espalda, rodillas, etc.)?",
        "explicaciones": {
            0: "Dolor intenso. ➝ Te distrae constantemente, casi imposible concentrarte.",
            1: "Dolor moderado. ➝ Molestias que quitan parte de la concentración, se nota en cada bloque.",
            2: "Molestia leve. ➝ Apenas interfiere, puedes estudiar bien con pequeñas incomodidades.",
            3: "Sin molestias. ➝ Estás cómodo, postura estable, nada te resta concentración física."
        }
    },
    {
        "key": "concentracion",
        "titulo": "4. Concentración (20%)",
        "peso": 20.0,
        "pregunta": "¿Cómo notas tu capacidad de mantener la atención ahora mismo?",
        "explicaciones": {
            0: "Atención nula. ➝ No logras fijar la mente ni en 5 minutos, estudiar sería tiempo perdido.",
            1: "Muy disperso. ➝ Te distraes fácil, cuesta entrar en modo estudio.",
            2: "Atención aceptable. ➝ Puedes concentrarte, aunque con esfuerzo extra y riesgo de distracciones.",
            3: "Atención alta. ➝ Mente clara, puedes sumergirte en el estudio sin apenas dispersión."
        }
    },
    {
        "key": "memoria",
        "titulo": "5. Memoria activa (10%)",
        "peso": 10.0,
        "pregunta": "¿Cómo notas tu capacidad de recordar lo que estudiaste ayer o recientemente?",
        "explicaciones": {
            0: "Muy mala memoria. ➝ Casi no recuerdas nada, incluso lo básico se te escapa.",
            1: "Memoria floja. ➝ Recuerdas fragmentos sueltos, con bastante esfuerzo.",
            2: "Memoria aceptable. ➝ Retienes lo esencial, aunque pierdes algunos detalles.",
            3: "Memoria fresca. ➝ Recuerdas fácilmente lo que estudiaste, lo tienes “a mano” en la mente."
        }
    },
    {
        "key": "agilidad",
        "titulo": "6. Agilidad mental (5%)",
        "peso": 5.0,
        "pregunta": "¿Cómo notas tu rapidez para procesar ideas y relacionar conceptos?",
        "explicaciones": {
            0: "Muy lento. ➝ Te cuesta incluso resolver ideas simples o seguir un hilo lógico.",
            1: "Lento. ➝ Procesas la información, pero con bastante esfuerzo y demora.",
            2: "Normal. ➝ Funcionas bien, aunque no con máxima claridad.",
            3: "Ágil. ➝ Piensas rápido, conectas ideas y entiendes conceptos al vuelo."
        }
    },
    {
        "key": "motivacion",
        "titulo": "7. Motivación (20%)",
        "peso": 20.0,
        "pregunta": "¿Qué ganas tienes de ponerte a estudiar hoy?",
        "explicaciones": {
            0: "Sin motivación. ➝ Te costará sentarte, resistencia interna muy alta.",
            1: "Ganas bajas. ➝ Lo harás por obligación, con poca energía mental.",
            2: "Motivación aceptable. ➝ Quieres avanzar, aunque no con todo el entusiasmo.",
            3: "Muy motivado. ➝ Ves el objetivo claro y estudias con energía y constancia."
        }
    },
    {
        "key": "estres",
        "titulo": "8. Estrés / Ansiedad (7,5%)",
        "peso": 7.5,
        "pregunta": "¿Cómo te notas en cuanto a nervios o presión hoy?",
        "explicaciones": {
            0: "Estrés extremo. ➝ La ansiedad bloquea tu capacidad de concentración y memoria.",
            1: "Estrés notable. ➝ Tensión clara que interfiere en tu rendimiento.",
            2: "Estrés moderado. ➝ Notas cierta presión, pero manejable.",
            3: "Serenidad. ➝ Estado tranquilo y estable, condiciones óptimas para estudiar."
        }
    },
    {
        "key": "animo",
        "titulo": "9. Estado de ánimo (2,5%)",
        "peso": 2.5,
        "pregunta": "¿Cómo te notas en cuanto a humor y emociones hoy?",
        "explicaciones": {
            0: "Muy bajo. ➝ Apatía, desgana total, difícil mantener la constancia.",
            1: "Ánimo bajo. ➝ Falta de entusiasmo, cuesta empezar y mantener el ritmo.",
            2: "Ánimo neutro. ➝ Normal, ni positivo ni negativo, puedes rendir bien.",
            3: "Ánimo positivo. ➝ Optimista, predispuesto a estudiar, con buena energía emocional."
        }
    },
    {
        "key": "alimentacion",
        "titulo": "10. Alimentación / Hidratación (2,5%)",
        "peso": 2.5,
        "pregunta": "¿Cómo has empezado el día en este aspecto?",
        "explicaciones": {
            0: "Muy mal. ➝ Sin comer ni beber, sin energía mínima para rendir.",
            1: "Flojo. ➝ Comida insuficiente o pesada que resta energía.",
            2: "Aceptable. ➝ Has comido/bebido lo suficiente, aunque mejorable.",
            3: "Bien. ➝ Buena nutrición e hidratación, energía estable y sin pesadez."
        }
    }
]

PESOS_TOTAL = sum(item["peso"] for item in ITEMS)
assert abs(PESOS_TOTAL - 100.0) < 1e-6, "Los pesos no suman 100%"

# ---------------------------
# Estado de sesión
# ---------------------------
if "paso" not in st.session_state:
    st.session_state.paso = 0
if "respuestas" not in st.session_state:
    st.session_state.respuestas = {item["key"]: None for item in ITEMS}
if "historial" not in st.session_state:
    st.session_state.historial = []  # lista de dicts

# ---------------------------
# Funciones
# ---------------------------

def calcular_porcentaje(respuestas):
    total = 0.0
    for item in ITEMS:
        val = respuestas.get(item["key"], 0.0)
        # clamp input a [0,3]
        val = max(0.0, min(3.0, float(val)))
        contrib = (val / 3.0) * item["peso"]
        total += contrib
    # redondeo 1 decimal y límites
    total = round(min(100.0, max(0.0, total)), 1)
    return total

def color_y_horas(pct):
    if pct >= 85.0:
        return ("Verde", "5–6 h netas. Día para temas nuevos + repasos exigentes.")
    if pct >= 70.0:
        return ("Amarillo", "3–4 h netas. Prioriza lo importante.")
    if pct >= 50.0:
        return ("Naranja", "2–3 h suaves. Repasos y tareas ligeras.")
    return ("Rojo", "1–2 h muy ligeras o descanso.")

def simular_curva(pct_inicial, horas_total, pendiente_fatiga, dur_pomo, descanso_corto, descanso_largo, suelo_corto, suelo_largo):
    """
    Devuelve tiempos (en horas) y productividad (%) según patrón de pomodoros 3×25' + descansos (5/5/30), repetido.
    - El 'techo' cae linealmente: techo(t) = max(0, pct_inicial - pendiente_fatiga * t_horas)
    - Dentro de cada pomodoro hacemos una 'joroba' suave: sube rápido y decae suavemente.
    - Descansos: niveles planos como fracción del techo.
    """
    minutos_total = int(horas_total * 60)
    t = np.arange(0, minutos_total + 1)  # minuto a minuto
    y = np.zeros_like(t, dtype=float)

    # Patrón por ciclo: estudio, descanso corto, estudio, descanso corto, estudio, descanso largo
    pattern = [
        ("study", dur_pomo),
        ("short", descanso_corto),
        ("study", dur_pomo),
        ("short", descanso_corto),
        ("study", dur_pomo),
        ("long", descanso_largo),
    ]

    idx = 0
    while idx < len(t):
        for tipo, dur in pattern:
            if idx >= len(t):
                break
            tramo = min(dur, len(t) - idx)
            for j in range(tramo):
                minutos_abs = idx + j
                horas_abs = minutos_abs / 60.0
                techo = max(0.0, pct_inicial - pendiente_fatiga * horas_abs)
                if tipo == "study":
                    # Curva "joroba": arranque rápido y declive suave hacia el final del pomodoro
                    s = j / float(max(1, dur - 1))  # 0..1
                    # Arranque con impulso (primeros 3 minutos recuperas)
                    if j < min(3, dur):
                        ramp = 0.85 + 0.15 * (j / float(max(1, 3 - 1)))  # 0.85->1.0
                    else:
                        ramp = 1.0
                    # Decaimiento suave hasta ~0.85 del techo al final
                    decaimiento = 1.0 - 0.15 * s
                    y[minutos_abs] = techo * ramp * decaimiento
                elif tipo == "short":
                    y[minutos_abs] = techo * suelo_corto
                else:  # long
                    y[minutos_abs] = techo * suelo_largo
            idx += tramo
            if idx >= len(t):
                break

    return t / 60.0, y

def mostrar_resultados(pct, color, recomendacion, serie_t, serie_y):
    st.subheader("Resultados del día")
    c1, c2, c3 = st.columns(3)
    c1.metric("Productividad ponderada", f"{pct:.1f}%")
    c2.metric("Color", color)
    c3.metric("Horas recomendadas", recomendacion.split(".")[0] + ".")

    st.write(f"**Recomendación:** {recomendacion}")

    # Gráfica Matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(serie_t, serie_y, label=f"Inicio: {pct:.1f}%", linewidth=2.0)
    ax.axhline(50, linestyle="--", color="black", label="Umbral 50%")
    ax.set_title(f"Curva de productividad personalizada ({dt.date.today().isoformat()})")
    ax.set_xlabel("Horas de estudio")
    ax.set_ylabel("Productividad relativa (%)")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, max(105, max(serie_y) + 5))
    ax.set_xlim(0, serie_t[-1] if len(serie_t) else 8)
    ax.legend(loc="upper right")
    st.pyplot(fig, clear_figure=True)

    # Botón para descargar PNG
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    st.download_button("⬇️ Descargar gráfica (PNG)", data=buf.getvalue(), file_name=f"curva_productividad_{dt.date.today().isoformat()}.png", mime="image/png")

# ---------------------------
# UI flujo paso a paso
# ---------------------------
st.markdown("**Flujo diario:** pulsa “Empezar test” y responde a las 10 preguntas (0–3, se aceptan decimales como 2.5).")

if st.button("🟢 Empezar test", disabled=st.session_state.paso>0):
    st.session_state.paso = 1

if 1 <= st.session_state.paso <= len(ITEMS):
    idx = st.session_state.paso - 1
    item = ITEMS[idx]

    st.markdown(f"### {item['titulo']}")
    st.write(item["pregunta"])

    with st.expander("¿Qué significa 0–3 exactamente?"):
        for k in [0, 1, 2, 3]:
            st.markdown(f"**{k} →** {item['explicaciones'][k]}")

    val = st.number_input("Tu puntuación (0–3, acepta decimales)", min_value=0.0, max_value=3.0, step=0.1, key=f"input_{item['key']}")

    cols = st.columns([1,1,1])
    if cols[0].button("⟵ Atrás", disabled=st.session_state.paso == 1):
        st.session_state.paso -= 1
        st.stop()

    if cols[1].button("Guardar respuesta"):
        st.session_state.respuestas[item["key"]] = float(val)

    if cols[2].button("Siguiente ⟶"):
        if st.session_state.respuestas[item["key"]] is None:
            st.warning("Guarda la respuesta antes de continuar.")
            st.stop()
        st.session_state.paso += 1
        st.stop()

elif st.session_state.paso > len(ITEMS):
    # Calcular resultados
    pct = calcular_porcentaje(st.session_state.respuestas)
    color, recomendacion = color_y_horas(pct)

    # Simular curva
    t_h, y_pct = simular_curva(
        pct_inicial=pct,
        horas_total=horas_totales,
        pendiente_fatiga=pendiente_fatiga,
        dur_pomo=dur_pomo,
        descanso_corto=descanso_corto,
        descanso_largo=descanso_largo,
        suelo_corto=suelo_descanso_corto,
        suelo_largo=suelo_descanso_largo,
    )

    mostrar_resultados(pct, color, recomendacion, t_h, y_pct)

    # Guardar en historial
    if st.button("💾 Guardar en historial de hoy"):
        entrada = {
            "fecha": dt.date.today().isoformat(),
            "porcentaje": pct,
            "color": color,
            "recomendacion": recomendacion,
            "respuestas": st.session_state.respuestas.copy(),
            "parametros": {
                "horas_totales": horas_totales,
                "pendiente_fatiga": pendiente_fatiga,
                "dur_pomo": dur_pomo,
                "descanso_corto": descanso_corto,
                "descanso_largo": descanso_largo,
                "suelo_descanso_corto": suelo_descanso_corto,
                "suelo_descanso_largo": suelo_descanso_largo,
            }
        }
        st.session_state.historial.append(entrada)
        st.success("Guardado en historial.")

    # Mostrar/descargar historial
    if st.session_state.historial:
        st.subheader("Historial")
        st.dataframe(st.session_state.historial, use_container_width=True)
        import json
        st.download_button(
            "⬇️ Descargar historial (JSON)",
            data=json.dumps(st.session_state.historial, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="historial_productividad.json",
            mime="application/json"
        )

    # Reiniciar
    if st.button("🔁 Reiniciar test"):
        st.session_state.paso = 0
        st.session_state.respuestas = {item["key"]: None for item in ITEMS}
        st.experimental_rerun()

else:
    st.info("Pulsa **Empezar test** para iniciar.")
