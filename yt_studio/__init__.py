"""
yt-studio - A visualization tool for QUOKKA simulation data
============================================================

This package provides both a Python library (plot_quokka) and a web-based
interface for visualizing QUOKKA AMR simulation data.

To start the web interface:
    $ yt-studio

To use the Python library:
    >>> from plot_quokka import QuokkaPlotter
    >>> plotter = QuokkaPlotter("data/plt00020")
    >>> plotter.slice("z", "density", output="output.png")
"""

__version__ = "2.0.0"
