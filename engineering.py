"""
engineering.py
================
Core engineering classes for the Fluid Flow & Heat Transfer Engineering Suite.

This module keeps all physics/engineering calculations separate from the
Streamlit UI code (app.py and the files in pages/). Each class is
documented, uses sensible SI units internally, and raises clear errors
on invalid input so the UI layer can catch and display them nicely.

Author: <your name here>
"""

import math


# ---------------------------------------------------------------------------
# Reference fluid property library (SI units)
#   density   -> kg/m^3
#   viscosity -> Pa.s (dynamic viscosity)
# Values are typical properties at ~20 C / 1 atm and are good enough for a
# course-level calculator. Real engineering work would look these up from
# temperature-dependent property tables.
# ---------------------------------------------------------------------------
FLUID_LIBRARY = {
    "Water": {"density": 998.0, "viscosity": 1.002e-3},
    "Air": {"density": 1.204, "viscosity": 1.825e-5},
    "Crude Oil": {"density": 870.0, "viscosity": 8.0e-3},
}


class Fluid:
    """
    Represents a fluid with density and dynamic viscosity.

    A Fluid can either be created from the built-in FLUID_LIBRARY
    (water, air, crude oil) or as a fully user-defined fluid by supplying
    density and viscosity directly.
    """

    def __init__(self, name: str, density: float = None, viscosity: float = None):
        """
        Create a Fluid.

        Parameters
        ----------
        name : str
            Name of the fluid. If it matches a key in FLUID_LIBRARY
            (case-insensitive) its properties are looked up automatically.
            Any other name is treated as a "user-defined" fluid and
            density/viscosity must be supplied.
        density : float, optional
            Fluid density in kg/m^3. Required for user-defined fluids.
        viscosity : float, optional
            Dynamic viscosity in Pa.s. Required for user-defined fluids.

        Raises
        ------
        ValueError
            If the fluid is not in the library and density/viscosity are
            not both supplied, or if supplied values are not positive.
        """
        self.name = name
        lookup_key = None
        for key in FLUID_LIBRARY:
            if key.lower() == str(name).lower():
                lookup_key = key
                break

        if lookup_key is not None:
            props = FLUID_LIBRARY[lookup_key]
            self.density = props["density"] if density is None else density
            self.viscosity = props["viscosity"] if viscosity is None else viscosity
        else:
            if density is None or viscosity is None:
                raise ValueError(
                    f"'{name}' is not a built-in fluid. Please supply both "
                    f"density and viscosity for a user-defined fluid."
                )
            self.density = density
            self.viscosity = viscosity

        if self.density <= 0:
            raise ValueError("Fluid density must be a positive number (kg/m^3).")
        if self.viscosity <= 0:
            raise ValueError("Fluid viscosity must be a positive number (Pa.s).")

    def __repr__(self):
        return f"Fluid(name={self.name!r}, density={self.density}, viscosity={self.viscosity})"


class Pipe:
    """
    Represents a circular pipe carrying a Fluid and performs the standard
    pipe-flow hydraulics calculations used in Module A (Pipe Flow Analyser):
    velocity, Reynolds number, Darcy friction factor and pressure drop.
    """

    def __init__(self, diameter: float, length: float, roughness: float, fluid: Fluid):
        """
        Create a Pipe.

        Parameters
        ----------
        diameter : float
            Internal pipe diameter in metres (m). Must be > 0.
        length : float
            Pipe length in metres (m). Must be > 0.
        roughness : float
            Absolute internal wall roughness in metres (m). Must be >= 0.
        fluid : Fluid
            The Fluid instance flowing through the pipe.

        Raises
        ------
        ValueError
            If diameter/length are not positive, roughness is negative,
            or fluid is not a Fluid instance.
        """
        if diameter <= 0:
            raise ValueError("Pipe diameter must be positive (m).")
        if length <= 0:
            raise ValueError("Pipe length must be positive (m).")
        if roughness < 0:
            raise ValueError("Pipe roughness cannot be negative (m).")
        if not isinstance(fluid, Fluid):
            raise ValueError("fluid must be a Fluid instance.")

        self.diameter = diameter
        self.length = length
        self.roughness = roughness
        self.fluid = fluid

    @property
    def area(self) -> float:
        """Cross-sectional flow area in m^2."""
        return math.pi * (self.diameter ** 2) / 4.0

    def velocity(self, flow_rate: float) -> float:
        """
        Mean flow velocity for a given volumetric flow rate.

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s. Must be > 0.

        Returns
        -------
        float
            Mean velocity in m/s.
        """
        if flow_rate <= 0:
            raise ValueError("Flow rate must be positive (m^3/s).")
        return flow_rate / self.area

    def reynolds_number(self, flow_rate: float) -> float:
        """
        Reynolds number Re = rho * v * D / mu (dimensionless).

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.
        """
        v = self.velocity(flow_rate)
        return (self.fluid.density * v * self.diameter) / self.fluid.viscosity

    def friction_factor(self, flow_rate: float) -> float:
        """
        Darcy friction factor.

        Uses f = 64/Re for laminar flow (Re < 2300).
        Uses the Swamee-Jain explicit approximation to the Colebrook
        equation for turbulent flow (Re >= 2300):

            f = 0.25 / [ log10( (eps/(3.7*D)) + 5.74/Re^0.9 ) ]^2

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.
        """
        re = self.reynolds_number(flow_rate)
        if re < 2300:
            return 64.0 / re
        rel_roughness = self.roughness / self.diameter
        denom = math.log10((rel_roughness / 3.7) + (5.74 / (re ** 0.9)))
        return 0.25 / (denom ** 2)

    def pressure_drop(self, flow_rate: float) -> float:
        """
        Pressure drop along the pipe using the Darcy-Weisbach equation:

            dP = f * (L/D) * (rho * v^2 / 2)

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s.

        Returns
        -------
        float
            Pressure drop in Pascals (Pa).
        """
        v = self.velocity(flow_rate)
        f = self.friction_factor(flow_rate)
        return f * (self.length / self.diameter) * (self.fluid.density * v ** 2 / 2.0)

    def summary(self, flow_rate: float) -> dict:
        """
        Convenience method returning velocity, Re, friction factor and
        pressure drop for a given flow rate as a single dictionary.
        """
        return {
            "velocity_m_s": self.velocity(flow_rate),
            "reynolds_number": self.reynolds_number(flow_rate),
            "friction_factor": self.friction_factor(flow_rate),
            "pressure_drop_Pa": self.pressure_drop(flow_rate),
        }


class HeatExchanger:
    """
    Performs the two heat-transfer calculations used in Module B
    (Heat Transfer Calculator):

    1. Steady-state 1-D conduction through a single-layer flat wall
       (Fourier's Law).
    2. Newton's Law of Cooling: time for an object to cool from an
       initial temperature to a target temperature in a fixed-temperature
       ambient environment, plus the temperature-vs-time curve.
    """

    def __init__(self):
        """HeatExchanger has no persistent state; each method is a
        standalone calculation with its own inputs. Kept as a class
        (rather than free functions) to satisfy the OOP requirement and
        to group these two related physical models together."""
        pass

    @staticmethod
    def conduction_heat_flow(k: float, area: float, thickness: float,
                              t_hot: float, t_cold: float) -> float:
        """
        Steady-state conduction through a single-layer flat wall
        (Fourier's Law): Q = k * A * (T_hot - T_cold) / L

        Parameters
        ----------
        k : float
            Thermal conductivity of the wall material, W/(m.K). Must be > 0.
        area : float
            Cross-sectional area of the wall, m^2. Must be > 0.
        thickness : float
            Wall thickness, m. Must be > 0.
        t_hot : float
            Hot-side surface temperature, deg C (or K, as long as consistent).
        t_cold : float
            Cold-side surface temperature, same units as t_hot.

        Returns
        -------
        float
            Steady-state heat flow rate, Watts (W). Positive if t_hot > t_cold.
        """
        if k <= 0:
            raise ValueError("Thermal conductivity k must be positive (W/m.K).")
        if area <= 0:
            raise ValueError("Area must be positive (m^2).")
        if thickness <= 0:
            raise ValueError("Wall thickness must be positive (m).")
        return k * area * (t_hot - t_cold) / thickness

    @staticmethod
    def cooling_time(t0: float, t_target: float, t_inf: float,
                      h: float, area: float, mass: float, cp: float) -> float:
        """
        Time required for a lumped object to cool from T0 to T_target in
        an ambient environment at T_inf, using Newton's Law of Cooling:

            T(t) = T_inf + (T0 - T_inf) * exp( -h*A / (m*cp) * t )

        Solved for t:

            t = -(m*cp) / (h*A) * ln( (T_target - T_inf) / (T0 - T_inf) )

        Parameters
        ----------
        t0 : float
            Initial object temperature (deg C).
        t_target : float
            Target object temperature (deg C). Must lie strictly between
            t_inf and t0 for a finite, physically meaningful cooling time.
        t_inf : float
            Ambient temperature (deg C).
        h : float
            Convective heat transfer coefficient, W/(m^2.K). Must be > 0.
        area : float
            Surface area of the object, m^2. Must be > 0.
        mass : float
            Mass of the object, kg. Must be > 0.
        cp : float
            Specific heat capacity of the object, J/(kg.K). Must be > 0.

        Returns
        -------
        float
            Time to reach t_target, in seconds.
        """
        if h <= 0 or area <= 0 or mass <= 0 or cp <= 0:
            raise ValueError("h, area, mass and cp must all be positive.")
        if t0 == t_inf:
            raise ValueError("Initial temperature must differ from ambient temperature.")

        # Object must be cooling towards T_inf, and target must sit between
        # T_inf and T0 (exclusive) or the exponential model gives no
        # finite/physical solution.
        if t0 > t_inf:
            if not (t_inf < t_target < t0):
                raise ValueError(
                    "Target temperature must lie strictly between ambient and "
                    "initial temperature for the object to cool towards it."
                )
        else:
            if not (t0 < t_target < t_inf):
                raise ValueError(
                    "Target temperature must lie strictly between initial and "
                    "ambient temperature for the object to warm towards it."
                )

        ratio = (t_target - t_inf) / (t0 - t_inf)
        return -(mass * cp) / (h * area) * math.log(ratio)

    @staticmethod
    def temperature_curve(t0: float, t_inf: float, h: float, area: float,
                           mass: float, cp: float, t_end: float, n_points: int = 200):
        """
        Generate a temperature-vs-time curve for Newton's Law of Cooling.

        Parameters
        ----------
        t0, t_inf, h, area, mass, cp : float
            See cooling_time() for definitions.
        t_end : float
            End time of the curve, seconds. Must be > 0.
        n_points : int
            Number of points to generate (default 200).

        Returns
        -------
        (list, list)
            Tuple of (time_seconds, temperature) lists, suitable for plotting.
        """
        if h <= 0 or area <= 0 or mass <= 0 or cp <= 0:
            raise ValueError("h, area, mass and cp must all be positive.")
        if t_end <= 0:
            raise ValueError("t_end must be positive (s).")

        k_const = h * area / (mass * cp)
        times = [t_end * i / (n_points - 1) for i in range(n_points)]
        temps = [t_inf + (t0 - t_inf) * math.exp(-k_const * t) for t in times]
        return times, temps
