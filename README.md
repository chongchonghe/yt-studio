# yt-studio

A visualization tool for [QUOKKA](https://github.com/quokka-astro/quokka) simulation data with both a web interface and Python API.

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+ (for web interface)

### Install

```bash
pip install git+https://github.com/chongchonghe/yt-studio.git
```

or install from source:

```bash
# Clone the repository
git clone https://github.com/chongchonghe/yt-studio.git
cd yt-studio

# Install in development mode
pip install -e .
```

## Usage

### Web Interface

Start the visualization servers:

```bash
yt-studio
```

Then open http://localhost:5173 in your browser.

**Options:**
```bash
yt-studio --backend-port 8080    # Custom backend port
yt-studio --frontend-port 3000   # Custom frontend port
yt-studio --backend-only         # API server only (no frontend)
```

### Python API

```python
from plot_quokka import QuokkaPlotter, PlotParams

# Load a dataset
plotter = QuokkaPlotter("/path/to/plt00020")

# Create a slice plot
plotter.slice("z", "density", output="density_slice.png")

# Create a projection plot
plotter.project("z", "density", output="density_projection.png")

# Customize with parameters
params = PlotParams(cmap="inferno", log_scale=True, dpi=300)
params.colorbar.show = True
params.scale_bar.show = True
plotter.slice("z", "density", params=params, output="custom_slice.png")
```

## Features

- **Slice plots** - 2D cross-sections through simulation data
- **Projection plots** - Line-of-sight integrations with optional weighting
- **Volume rendering** - 3D visualizations with customizable camera
- **Multiple colormaps** - viridis, plasma, inferno, magma, and more
- **Annotations** - Colorbar, scale bar, timestamp, AMR grid overlay
- **Particle overlay** - Visualize particle data on plots
- **High-resolution export** - Publication-quality PNG export (300 DPI)

## License

MIT License
