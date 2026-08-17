"""
app.py
======
Home page for the Fluid Flow & Heat Transfer Engineering Suite.

This is the entry point for the multi-page Streamlit application.
Run it with:  streamlit run app.py

The three functional modules live in the pages/ folder and are
auto-discovered by Streamlit's multi-page app feature:
    pages/1_Pipe_Flow_Analyser.py
    pages/2_Heat_Transfer_Calculator.py
    pages/3_Rock_Fluid_Dashboard.py

All engineering calculations live in engineering.py (OOP: Fluid, Pipe,
HeatExchanger classes) and are imported by the pages, not re-implemented.
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Engineering Suite",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Fluid Flow & Heat Transfer Engineering Suite")

st.markdown(
    """
Welcome! This application bundles three engineering calculation tools into
a single suite, built for **PE 262 - Computer Programming (Capstone
Project)**.

Use the sidebar (or the links below) to navigate to a module:
"""
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📏 Pipe Flow Analyser")
    st.write(
        "Calculate velocity, Reynolds number, friction factor and "
        "pressure drop for flow through a pipe, using the Darcy-Weisbach "
        "equation. Supports water, air, crude oil, or a custom fluid."
    )
    st.page_link("pages/1_Pipe_Flow_Analyser.py", label="Open Pipe Flow Analyser →")

with col2:
    st.subheader("🌡️ Heat Transfer Calculator")
    st.write(
        "Calculate steady-state conduction through a flat wall (Fourier's "
        "Law) and the time needed for an object to cool in an ambient "
        "environment (Newton's Law of Cooling), with a live cooling curve."
    )
    st.page_link("pages/2_Heat_Transfer_Calculator.py", label="Open Heat Transfer Calculator →")

with col3:
    st.subheader("🪨 Rock & Fluid Data Dashboard")
    st.write(
        "Upload a CSV of rock or fluid core data, view summary statistics, "
        "filter by porosity, and explore a porosity histogram and a "
        "porosity-permeability crossplot."
    )
    st.page_link("pages/3_Rock_Fluid_Dashboard.py", label="Open Rock & Fluid Dashboard →")

st.divider()

st.markdown(
    """
### About this app
This suite was built to demonstrate everything covered in PE 262:
computational thinking, Python, data analysis, object-oriented
programming, AI-assisted development, and deployment on Streamlit
Community Cloud.

All engineering calculations (fluid properties, pipe hydraulics, and
heat transfer models) are implemented as classes in `engineering.py`,
kept separate from the page/UI code for clarity and reuse.

See the project `README.md` on GitHub for setup instructions, a
description of each module, and documentation of how AI tools were
used during development.
"""
)
