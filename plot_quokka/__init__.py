"""
plot_quokka - A generic QUOKKA simulation visualization library
================================================================

This module provides visualization tools for QUOKKA AMR simulation data.
It can be used standalone in Python/Jupyter or with the web frontend.

Usage Examples
--------------

Basic slice plot:
>>> from plot_quokka import QuokkaPlotter
>>> plotter = QuokkaPlotter("data/plt00020")
>>> plotter.slice("z", "density", output="output.png")

Projection plot:
>>> plotter.project("z", "density", weight_field="density")

Volume rendering:
>>> plotter.volume("density", camera_theta=45, camera_phi=30)

With custom parameters:
>>> from plot_quokka import PlotParams, ColorbarParams
>>> params = PlotParams(
...     cmap="inferno",
...     log_scale=True,
...     vmin=1e-20,
...     vmax=1e-15,
...     colorbar=ColorbarParams(show=True, label="Density")
... )
>>> plotter.slice("z", "density", params=params)
"""

from .config import PlotConfig, load_config
from .params import (
    PlotParams,
    ColorbarParams,
    ScaleBarParams,
    AnnotationParams,
    ParticleParams,
    VolumeRenderParams,
    WidthParams,
)
from .dataset import QuokkaDataset
from .plotting import QuokkaPlotter

__version__ = "2.0.0"
__all__ = [
    # Main interface
    "QuokkaPlotter",
    "QuokkaDataset",
    # Configuration
    "PlotConfig",
    "load_config",
    # Parameter classes
    "PlotParams",
    "ColorbarParams",
    "ScaleBarParams",
    "AnnotationParams",
    "ParticleParams",
    "VolumeRenderParams",
    "WidthParams",
]
