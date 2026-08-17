"""
Module A: Pipe Flow Analyser

A complete pipe-flow calculator. The user selects a fluid (water, air,
crude oil, or a user-defined fluid), enters pipe geometry and a flow
rate, and gets velocity, Reynolds number, friction factor and pressure
drop, plus an interactive plot of pressure drop vs flow rate and a CSV
export of that curve.
"""

import io
import sys
import os

import pandas as pd
import streamlit as st

# Allow importing engineering.py from the project root when Streamlit
# runs this file directly from the pages/ folder.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engineering import Fluid, Pipe, FLUID_LIBRARY

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="📏", layout="wide")
st.title("📏 Pipe Flow Analyser")
st.caption(
    "Darcy-Weisbach pressure drop calculator for flow through a circular pipe."
)

# ---------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------
st.sidebar.header("Inputs")

fluid_choice = st.sidebar.selectbox(
    "Fluid",
    list(FLUID_LIBRARY.keys()) + ["User-defined"],
    help="Choose a built-in fluid (properties auto-populate below) or "
         "'User-defined' to enter your own density and viscosity.",
)

if fluid_choice == "User-defined":
    density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.001, value=1000.0, step=1.0,
        help="Mass per unit volume of the fluid.",
    )
    viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa·s)", min_value=1e-6, value=1.0e-3,
        step=1e-4, format="%.6f",
        help="Resistance of the fluid to flow/shear.",
    )
    fluid_name = "User-defined fluid"
else:
    props = FLUID_LIBRARY[fluid_choice]
    density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.001, value=float(props["density"]), step=1.0,
        help="Auto-populated for the selected fluid; feel free to override.",
    )
    viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa·s)", min_value=1e-6, value=float(props["viscosity"]),
        step=1e-5, format="%.6f",
        help="Auto-populated for the selected fluid; feel free to override.",
    )
    fluid_name = fluid_choice

st.sidebar.divider()
st.sidebar.subheader("Pipe geometry")

diameter_mm = st.sidebar.number_input(
    "Internal diameter D (mm)", min_value=1.0, value=50.0, step=1.0,
    help="Internal diameter of the pipe, in millimetres.",
)
length_m = st.sidebar.number_input(
    "Pipe length L (m)", min_value=0.01, value=10.0, step=1.0,
    help="Total straight-line length of the pipe run, in metres.",
)
roughness_mm = st.sidebar.number_input(
    "Absolute roughness ε (mm)", min_value=0.0, value=0.0015, step=0.0005,
    format="%.4f",
    help="Internal wall roughness. Typical: commercial steel ≈ 0.0015 mm, "
         "PVC ≈ 0.0015 mm, cast iron ≈ 0.26 mm.",
)

st.sidebar.divider()
st.sidebar.subheader("Flow rate")

flow_rate_lpm = st.sidebar.number_input(
    "Flow rate Q (L/min)", min_value=0.01, value=300.0, step=10.0,
    help="Volumetric flow rate through the pipe, in litres per minute.",
)

# ---------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------
try:
    fluid = Fluid(fluid_name, density=density, viscosity=viscosity)
    pipe = Pipe(
        diameter=diameter_mm / 1000.0,
        length=length_m,
        roughness=roughness_mm / 1000.0,
        fluid=fluid,
    )
    flow_rate_m3s = flow_rate_lpm / 60000.0  # L/min -> m^3/s

    results = pipe.summary(flow_rate_m3s)

    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity", f"{results['velocity_m_s']:.3f} m/s")
    c2.metric("Reynolds number", f"{results['reynolds_number']:,.0f}")
    c3.metric("Friction factor (Darcy)", f"{results['friction_factor']:.5f}")
    c4.metric("Pressure drop", f"{results['pressure_drop_Pa']/1000:.3f} kPa")

    flow_regime = "Laminar" if results["reynolds_number"] < 2300 else "Turbulent"
    st.caption(f"Flow regime: **{flow_regime}** (Re = {results['reynolds_number']:,.0f})")

    st.divider()

    # -------------------------------------------------------------
    # Pressure drop vs flow rate curve
    # -------------------------------------------------------------
    st.subheader("Pressure drop vs flow rate")

    range_col1, range_col2 = st.columns(2)
    q_min_lpm = range_col1.number_input(
        "Range minimum (L/min)", min_value=0.01, value=max(flow_rate_lpm * 0.1, 0.01),
    )
    q_max_lpm = range_col2.number_input(
        "Range maximum (L/min)", min_value=q_min_lpm + 0.01, value=flow_rate_lpm * 2,
    )

    n_points = 50
    q_values_lpm = [
        q_min_lpm + i * (q_max_lpm - q_min_lpm) / (n_points - 1) for i in range(n_points)
    ]
    curve_rows = []
    for q_lpm in q_values_lpm:
        q_m3s = q_lpm / 60000.0
        s = pipe.summary(q_m3s)
        curve_rows.append(
            {
                "Flow rate (L/min)": q_lpm,
                "Velocity (m/s)": s["velocity_m_s"],
                "Reynolds number": s["reynolds_number"],
                "Friction factor": s["friction_factor"],
                "Pressure drop (kPa)": s["pressure_drop_Pa"] / 1000.0,
            }
        )
    curve_df = pd.DataFrame(curve_rows)

    st.line_chart(curve_df.set_index("Flow rate (L/min)")["Pressure drop (kPa)"])

    with st.expander("Show underlying data table"):
        st.dataframe(curve_df, use_container_width=True)

    # -------------------------------------------------------------
    # CSV export
    # -------------------------------------------------------------
    csv_buffer = io.StringIO()
    curve_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download pressure drop vs flow rate curve as CSV",
        data=csv_buffer.getvalue(),
        file_name="pipe_flow_pressure_drop_curve.csv",
        mime="text/csv",
    )

except ValueError as e:
    st.error(f"Input error: {e}")
