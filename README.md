# QUOKKA Visualization Tool v2

A modern, clean visualization tool for [QUOKKA](https://github.com/quokka-astro/quokka) simulation data. This tool provides both a Python module for scripting and a web-based interface for interactive exploration.

## Features

- **Slice plots** - 2D cross-sections through your simulation data
- **Projection plots** - Line-of-sight integrations with optional weighting
- **Volume rendering** - 3D visualizations with customizable camera angles
- **Multiple colormaps** - viridis, plasma, inferno, magma, and more
- **Annotations** - Colorbar, scale bar, timestamp, AMR grid overlay
- **Particles** - Overlay particle data on your plots
- **Animation** - Playback through multiple timesteps
- **Export** - High-resolution PNG export (300 DPI)

## Project Structure

```
quokka-vis-tool-v2/
├── plot_quokka/           # Python module (reusable)
│   ├── __init__.py        # Public API
│   ├── config.py          # Configuration management
│   ├── params.py          # Plot parameter dataclasses
│   ├── dataset.py         # Dataset loading & derived fields
│   └── plotting.py        # Core plotting logic
├── backend/
│   └── main.py            # FastAPI server
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # React application
│   │   ├── index.css      # Styling
│   │   └── main.jsx       # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── test.py                # Validation script
├── requirements.txt       # Python dependencies
└── README.md
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Clone and Setup Python Environment

```bash
cd quokka-vis-tool-v2

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Quick Start

### Option 1: Web Interface

You need to start **both** the backend and frontend servers:

#### Terminal 1 - Start Backend
```bash
cd quokka-vis-tool-v2
source .venv/bin/activate  # Activate your virtual environment
cd backend
python main.py
```

The backend will start on http://localhost:9010

#### Terminal 2 - Start Frontend
```bash
cd quokka-vis-tool-v2/frontend
npm run dev
```

The frontend will start on http://localhost:5173

**Open your browser to http://localhost:5173**

### Option 2: Python Script / Jupyter Notebook

```python
from plot_quokka import QuokkaPlotter, PlotParams

# Load dataset
plotter = QuokkaPlotter("/path/to/plt00020")

# Create a slice plot
plotter.slice("z", "density", output="density_slice.png")

# Create a projection plot
plotter.project("z", "density", output="density_projection.png")

# Customize with parameters
params = PlotParams(
    cmap="inferno",
    log_scale=True,
    dpi=300
)
params.colorbar.show = True
params.scale_bar.show = True

plotter.slice("z", "density", params=params, output="custom_slice.png")
```

## Usage Guide

### Web Interface

1. **Set Data Directory** - Click "DATA DIRECTORY" section and enter the path to your simulation outputs
2. **Select Dataset** - Use the dropdown at the bottom to choose a timestep
3. **Choose Plot Type** - Click Slice, Project, or 3D
4. **Select Field** - Choose from density, temperature, velocity, etc.
5. **Customize** - Adjust colormap, scale, display options
6. **Export** - Click "Export PNG (300 DPI)" for publication-quality output

### Python Module API

#### QuokkaPlotter

```python
from plot_quokka import QuokkaPlotter

plotter = QuokkaPlotter(dataset_path, config=None)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `slice(axis, field, params=None, output=None)` | Create a slice plot |
| `project(axis, field, params=None, weight_field=None, output=None)` | Create a projection plot |
| `volume(field, params=None, output=None)` | Create a volume rendering |
| `get_available_fields()` | List all available fields |

#### PlotParams

```python
from plot_quokka import PlotParams, ColorbarParams, ScaleBarParams

params = PlotParams(
    cmap="viridis",           # Colormap name
    log_scale=True,           # Use logarithmic scaling
    vmin=1e-24,               # Minimum value
    vmax=1e-20,               # Maximum value
    dpi=300,                  # Output resolution
    field_unit="g/cm**3",     # Convert to this unit
)

# Colorbar settings
params.colorbar.show = True
params.colorbar.label = "Density"
params.colorbar.orientation = "right"

# Scale bar settings
params.scale_bar.show = True
params.scale_bar.size = 10.0
params.scale_bar.unit = "kpc"

# Annotations
params.annotations.show_grids = True
params.annotations.show_timestamp = True
params.annotations.top_left_text = "My Simulation"

# Particles
params.particles.types = ["CIC_particles"]
params.particles.size = 5
params.particles.color = "red"

# Width/zoom
params.width.value = 100.0
params.width.unit = "kpc"

# Volume rendering
params.volume.camera_theta = 45.0
params.volume.camera_phi = 45.0
params.volume.n_layers = 5
params.volume.preview = True
```

### Available Fields

The tool automatically detects available fields from your dataset. Common fields include:

- `density` - Gas density
- `temperature` - Gas temperature (derived)
- `pressure` - Gas pressure
- `velocity_x`, `velocity_y`, `velocity_z` - Velocity components
- `velocity_magnitude` - Total velocity (derived)
- Particle fields (if present)

### Colormaps

Supported colormaps: `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `hot`, `jet`, `gray`, `coolwarm`, `RdBu`, `seismic`

## Configuration

Create a `config.yaml` file to customize default settings:

```yaml
# config.yaml
short_size: 3.6
font_size: 20
default_dpi: 300
cache_max_size: 32
show_axes: false
particle_types:
  - Rad
  - CIC
  - Sink
default_particle_size: 10
```

Load custom config:

```python
from plot_quokka import PlotConfig, load_config, QuokkaPlotter

config = load_config("config.yaml")
plotter = QuokkaPlotter("/path/to/data", config=config)
```

## Running Tests

Validate the installation with the test script:

```bash
cd quokka-vis-tool-v2
source .venv/bin/activate
python test.py
```

This will generate test outputs in the `output/` directory.

## Troubleshooting

### "Connection refused" errors in frontend

**Cause:** The backend server is not running.

**Solution:** Make sure to start the backend first:
```bash
cd backend && python main.py
```

### "No dataset loaded" error

**Cause:** You haven't loaded a dataset yet.

**Solution:** 
- Web: Set the data directory and select a dataset
- Python: Provide a valid path to `QuokkaPlotter()`

### "Module not found" errors

**Cause:** Dependencies not installed.

**Solution:**
```bash
pip install -r requirements.txt
```

### Slow volume rendering

**Cause:** High-resolution rendering takes time.

**Solution:** Enable "Preview mode" in the web interface, or set `params.volume.preview = True` in Python.

### Font/matplotlib warnings

These are harmless warnings about font caching. To suppress them:
```bash
export MPLCONFIGDIR=/tmp/matplotlib
```

## API Endpoints (Backend)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/server_info` | GET | Server information |
| `/api/set_data_dir` | POST | Set data directory |
| `/api/datasets` | GET | List available datasets |
| `/api/load_dataset` | POST | Load a specific dataset |
| `/api/fields` | GET | Get available fields |
| `/api/slice` | GET | Generate plot image |
| `/api/export/current_frame` | GET | Export high-res image |

## Development

### Frontend Development

```bash
cd frontend
npm run dev      # Development server with hot reload
npm run build    # Production build
npm run preview  # Preview production build
```

### Adding New Features

1. Add functionality to `plot_quokka/` module
2. Expose through `__init__.py`
3. Add API endpoint in `backend/main.py`
4. Update frontend in `frontend/src/App.jsx`

## License

MIT License

## Acknowledgments

- Built with [yt](https://yt-project.org/) for data analysis
- [FastAPI](https://fastapi.tiangolo.com/) for the backend
- [React](https://react.dev/) + [Vite](https://vitejs.dev/) for the frontend
