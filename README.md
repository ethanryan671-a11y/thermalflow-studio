# Fluid Flow & Heat Transfer Engineering Suite

**PE 262 — Computer Programming — Capstone Project**

A multi-page Streamlit engineering application combining pipe-flow
hydraulics, heat-transfer calculations, and a rock/fluid data dashboard
into one deployed, professional-quality tool.

🔗 **Live app:** https://thermalflow-studio-vblioixp9unsptc6bxnf2r.streamlit.app/

---

## What it does

| Module | Description |
|---|---|
| **A — Pipe Flow Analyser** | Select a fluid (water, air, crude oil, or user-defined), enter pipe geometry and flow rate, and get velocity, Reynolds number, Darcy friction factor, and pressure drop (Darcy-Weisbach equation). Includes an interactive pressure-drop-vs-flow-rate chart and CSV export. |
| **B — Heat Transfer Calculator** | Two calculators: (1) steady-state 1-D conduction through a single-layer flat wall (Fourier's Law), and (2) Newton's Law of Cooling — time to cool from an initial to a target temperature in a fixed ambient, with a live cooling curve. |
| **C — Rock & Fluid Data Dashboard** | Upload a CSV of rock/fluid core data, view summary statistics, filter by a porosity threshold, view a porosity histogram and a porosity-permeability crossplot, and download the filtered data. |
| **D — Code Quality & Deployment** | All engineering logic lives in `engineering.py` as documented classes (`Fluid`, `Pipe`, `HeatExchanger`), separate from the Streamlit UI code, with docstrings and input validation throughout. |

## Project structure

```
.
├── app.py                                 # Home page / entry point
├── engineering.py                         # OOP engineering classes (Fluid, Pipe, HeatExchanger)
├── requirements.txt
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py            # Module A
│   ├── 2_Heat_Transfer_Calculator.py      # Module B
│   └── 3_Rock_Fluid_Dashboard.py          # Module C
├── sample_data/
│   └── sample_rock_data.csv               # Example CSV for testing Module C
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Engineering methods used

- **Pipe flow:** cross-sectional area, velocity, Reynolds number
  `Re = ρvD/μ`; Darcy friction factor via `f = 64/Re` (laminar, Re <
  2300) or the Swamee-Jain explicit approximation to the Colebrook
  equation (turbulent); pressure drop via Darcy-Weisbach
  `ΔP = f(L/D)(ρv²/2)`.
- **Conduction:** Fourier's Law for a single-layer flat wall,
  `Q = kA(T_hot − T_cold)/L`.
- **Cooling:** Newton's Law of Cooling,
  `T(t) = T∞ + (T₀ − T∞)e^(−hA/(mc)·t)`, solved analytically for
  cooling time and used to generate the full temperature-vs-time curve.

All formulas were verified against hand calculations before being wired
into the UI (see the developer report for a worked example).

## AI usage documentation

AI assistance (Claude) was used during development. Below are the
prompts used, what was verified, and what was corrected, as required
by the assignment.

1. **Prompt:** "Write an OOP Fluid/Pipe class for pipe flow calculations
   (velocity, Reynolds number, Darcy friction factor via Colebrook/
   Swamee-Jain, Darcy-Weisbach pressure drop), with docstrings and
   input validation."
   - **Verified:** Recalculated velocity, Re, friction factor, and
     pressure drop by hand for water at D=50 mm, L=10 m, Q=5 L/s and
     confirmed the code's output matched (v ≈ 2.55 m/s, Re ≈ 126,800,
     ΔP ≈ 11.1 kPa).
   - **Corrected:** The initial version didn't switch between the
     laminar (`64/Re`) and turbulent (Swamee-Jain) friction-factor
     formulas — it used Swamee-Jain unconditionally, which is invalid
     below Re = 2300. Added the branch based on Reynolds number.

2. **Prompt:** "Write the Newton's Law of Cooling solver — given T0,
   Ttarget, Tinf, h, A, m, cp, return the time to reach Ttarget, and a
   function to generate the full temperature-vs-time curve."
   - **Verified:** Hand-solved the case T0=90°C, Ttarget=40°C,
     Tinf=20°C, h=10, A=0.5 m², m=1 kg, cp=4186 J/kg·K and got
     t ≈ 1049 s (≈17.5 min), matching the code's output exactly. Also
     checked the generated curve's final temperature equals the target.
   - **Corrected:** The first version didn't validate that the target
     temperature lies between the ambient and initial temperature, so
     an impossible target (e.g. cooling below ambient) produced a
     `math domain error` from `log()` of a negative/zero ratio instead
     of a clear message. Added an explicit range check with a readable
     `ValueError`.

3. **Prompt:** "Build a Streamlit page for the rock/fluid CSV dashboard
   that auto-detects porosity and permeability columns by name, handles
   messy/non-numeric values, and produces a histogram and crossplot."
   - **Verified:** Tested with `sample_data/sample_rock_data.csv`
     (60 synthetic rock samples) and confirmed the summary stats, the
     porosity filter slider, both charts, and the CSV download all
     worked correctly and matched a manual check in a spreadsheet.
   - **Corrected:** The column auto-detection originally matched on
     exact column names only (e.g. `"porosity"`), so a column named
     `"Porosity_frac"` wasn't found. Made the matching case-insensitive
     and substring-based, with a manual dropdown fallback if nothing
     matches.
