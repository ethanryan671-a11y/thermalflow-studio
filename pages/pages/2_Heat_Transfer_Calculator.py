"""
Module B: Heat Transfer Calculator

Two calculations:
  1. Steady-state conduction through a single-layer flat wall (Fourier's Law)
  2. Newton's Law of Cooling: time to cool from T0 to Ttarget in ambient
     Tinf, plus a live temperature-vs-time cooling curve.
"""

import sys
import os

import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engineering import HeatExchanger

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🌡️", layout="wide")
st.title("🌡️ Heat Transfer Calculator")
st.caption("Steady-state conduction and Newton's Law of Cooling.")

tab1, tab2 = st.tabs(["🧱 Conduction through a flat wall", "☕ Newton's Law of Cooling"])

# =======================================================================
# TAB 1: Conduction
# =======================================================================
with tab1:
    st.subheader("Steady-state conduction (Fourier's Law)")
    st.write(
        "Calculates the rate of heat flow through a single, uniform "
        "(single-layer) flat wall, given a temperature difference across "
        "its two faces: **Q = k · A · (T_hot − T_cold) / L**"
    )

    c1, c2 = st.columns(2)
    with c1:
        k = st.number_input(
            "Thermal conductivity, k (W/m·K)", min_value=0.0001, value=0.8,
            step=0.01,
            help="Property of the wall material. E.g. glass ≈ 0.8, "
                 "brick ≈ 0.7, insulation foam ≈ 0.03, steel ≈ 45.",
        )
        area = st.number_input(
            "Wall area, A (m²)", min_value=0.0001, value=2.0, step=0.1,
            help="Cross-sectional area through which heat flows.",
        )
        thickness_mm = st.number_input(
            "Wall thickness, L (mm)", min_value=0.01, value=5.0, step=1.0,
            help="Thickness of the wall in the direction of heat flow.",
        )
    with c2:
        t_hot = st.number_input(
            "Hot-side surface temperature (°C)", value=25.0, step=1.0,
            help="Temperature at the hotter face of the wall.",
        )
        t_cold = st.number_input(
            "Cold-side surface temperature (°C)", value=5.0, step=1.0,
            help="Temperature at the colder face of the wall.",
        )

    try:
        Q = HeatExchanger.conduction_heat_flow(
            k=k, area=area, thickness=thickness_mm / 1000.0,
            t_hot=t_hot, t_cold=t_cold,
        )
        st.metric("Heat flow rate, Q", f"{Q:,.2f} W")
        if Q < 0:
            st.info(
                "Q is negative, meaning heat actually flows from the "
                "'cold' side to the 'hot' side as entered — check which "
                "surface is hotter."
            )
    except ValueError as e:
        st.error(f"Input error: {e}")

# =======================================================================
# TAB 2: Newton's Law of Cooling
# =======================================================================
with tab2:
    st.subheader("Newton's Law of Cooling")
    st.write(
        "Calculates how long an object takes to cool from an initial "
        "temperature to a target temperature in a constant-temperature "
        "ambient environment: **T(t) = T∞ + (T₀ − T∞) · e^(−hA/(mc)·t)**"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        t0 = st.number_input(
            "Initial temperature, T₀ (°C)", value=90.0, step=1.0,
            help="Starting temperature of the object.",
        )
        t_inf = st.number_input(
            "Ambient temperature, T∞ (°C)", value=20.0, step=1.0,
            help="Temperature of the surrounding environment (assumed constant).",
        )
        t_target = st.number_input(
            "Target temperature (°C)", value=40.0, step=1.0,
            help="The temperature you want the object to reach. Must lie "
                 "strictly between T₀ and T∞.",
        )
    with c2:
        h = st.number_input(
            "Convection coefficient, h (W/m²·K)", min_value=0.01, value=10.0,
            step=1.0,
            help="Heat transfer coefficient between object and ambient air. "
                 "Still air ≈ 5-25, forced air ≈ 25-250.",
        )
        area_obj = st.number_input(
            "Surface area, A (m²)", min_value=0.0001, value=0.5, step=0.05,
            help="Exposed surface area of the cooling object.",
        )
    with c3:
        mass = st.number_input(
            "Mass, m (kg)", min_value=0.0001, value=1.0, step=0.1,
            help="Mass of the object.",
        )
        cp = st.number_input(
            "Specific heat capacity, c (J/kg·K)", min_value=0.1, value=4186.0,
            step=10.0,
            help="Specific heat of the object's material. Water ≈ 4186, "
                 "aluminium ≈ 900, steel ≈ 490.",
        )

    try:
        cooling_time_s = HeatExchanger.cooling_time(
            t0=t0, t_target=t_target, t_inf=t_inf, h=h, area=area_obj,
            mass=mass, cp=cp,
        )
        m1, m2 = st.columns(2)
        m1.metric("Time to reach target", f"{cooling_time_s:,.1f} s")
        m2.metric("", f"({cooling_time_s/60:,.2f} min)")

        st.divider()
        st.subheader("Cooling curve")

        curve_end_s = st.slider(
            "Curve duration to plot (s)",
            min_value=1.0,
            max_value=max(cooling_time_s * 3, 10.0),
            value=cooling_time_s * 1.5,
            help="Drag to extend/shorten how much of the cooling curve is plotted.",
        )

        times, temps = HeatExchanger.temperature_curve(
            t0=t0, t_inf=t_inf, h=h, area=area_obj, mass=mass, cp=cp,
            t_end=curve_end_s,
        )
        curve_df = pd.DataFrame({"Time (s)": times, "Temperature (°C)": temps})
        st.line_chart(curve_df.set_index("Time (s)"))

        with st.expander("Show underlying data table"):
            st.dataframe(curve_df, use_container_width=True)

    except ValueError as e:
        st.error(f"Input error: {e}")
