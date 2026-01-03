"""
FastAPI backend for QUOKKA Visualization Tool v2.

This backend uses the plot_quokka module to provide a clean API
for the web frontend.
"""

import os
import sys
import socket
import logging
import glob

# Add parent directory to path for plot_quokka module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from plot_quokka import (
    QuokkaPlotter,
    QuokkaDataset,
    PlotParams,
    PlotConfig,
    ColorbarParams,
    ScaleBarParams,
    AnnotationParams,
    ParticleParams,
    VolumeRenderParams,
    WidthParams,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress yt's verbose output
try:
    import yt
    yt.set_log_level(40)
except ImportError:
    pass

app = FastAPI(
    title="QUOKKA Visualization API",
    description="Clean API for visualizing QUOKKA simulation data",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
DATA_PATTERN = ""  # Glob pattern like ~/data/plt*
DATA_DIR = ""  # Base directory extracted from pattern
matched_datasets: List[str] = []  # Full paths to matched datasets
current_plotter: Optional[QuokkaPlotter] = None
current_dataset_name: Optional[str] = None

# Configuration
config = PlotConfig()


class DataPatternRequest(BaseModel):
    pattern: str


class PlotRequest(BaseModel):
    """Request model for plot generation."""
    axis: str = "z"
    field: str = "density"
    kind: str = "slc"  # slc, prj, vol
    weight_field: Optional[str] = None
    
    # Color settings
    cmap: str = "viridis"
    log_scale: bool = True
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    field_unit: Optional[str] = None
    
    # Display settings
    dpi: int = 150
    show_colorbar: bool = False
    colorbar_label: Optional[str] = None
    show_scale_bar: bool = False
    scale_bar_size: Optional[float] = None
    scale_bar_unit: Optional[str] = None
    
    # Width/zoom
    width_value: Optional[float] = None
    width_unit: Optional[str] = None
    
    # Annotations
    show_grids: bool = False
    show_timestamp: bool = False
    top_left_text: Optional[str] = None
    top_right_text: Optional[str] = None
    
    # Particles
    particles: Optional[str] = None
    particle_size: int = 10
    particle_color: str = "red"
    
    # Volume rendering
    camera_theta: float = 45.0
    camera_phi: float = 45.0
    n_layers: int = 5
    preview: bool = True
    show_box_frame: bool = False


@app.get("/")
def read_root():
    """Root endpoint with server info."""
    hostname = socket.gethostname()
    return {
        "name": "QUOKKA Visualization API",
        "version": "2.0.0",
        "hostname": hostname,
        "data_pattern": DATA_PATTERN,
        "current_dataset": current_dataset_name,
        "num_datasets": len(matched_datasets)
    }


@app.get("/api/server_info")
def get_server_info():
    """Get server information."""
    hostname = socket.gethostname()
    return {
        "hostname": hostname,
        "current_data_pattern": DATA_PATTERN,
        "num_datasets": len(matched_datasets),
        "current_dataset": current_dataset_name,
        "python_version": sys.version.split()[0]
    }


@app.post("/api/set_data_pattern")
def set_data_pattern(request: DataPatternRequest):
    """Set the data pattern (glob pattern like ~/data/plt*)."""
    global DATA_PATTERN, DATA_DIR, matched_datasets, current_plotter, current_dataset_name
    
    pattern = request.pattern.strip()
    
    # Expand ~ to home directory
    pattern = os.path.expanduser(pattern)
    
    # If pattern doesn't contain wildcards, treat as directory
    if '*' not in pattern and '?' not in pattern:
        # It's a plain directory path
        if os.path.isdir(pattern):
            # Add wildcard to match plt* inside
            pattern = os.path.join(pattern, "plt*")
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Path not found: {pattern}"
            )
    
    # Find matching paths
    matches = glob.glob(pattern)
    
    # Filter to only directories (datasets)
    matches = [m for m in matches if os.path.isdir(m)]
    matches.sort()
    
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No datasets found matching pattern: {pattern}"
        )
    
    DATA_PATTERN = request.pattern.strip()
    matched_datasets = matches
    current_plotter = None
    current_dataset_name = None
    
    # Extract base directory for display
    DATA_DIR = os.path.dirname(matches[0]) if matches else ""
    
    return {
        "message": f"Found {len(matches)} datasets",
        "pattern": DATA_PATTERN,
        "num_datasets": len(matches),
        "datasets": [os.path.basename(m) for m in matches[:10]],  # First 10 for preview
        "has_more": len(matches) > 10
    }


# Keep old endpoint for backward compatibility
@app.post("/api/set_data_dir")
def set_data_dir(request: DataPatternRequest):
    """Backward compatible endpoint - redirects to set_data_pattern."""
    return set_data_pattern(request)


@app.get("/api/datasets")
def get_datasets(prefix: str = ""):
    """List available datasets matching the current pattern."""
    if not matched_datasets:
        return {"datasets": []}
    
    # Return basenames of matched datasets
    datasets = [os.path.basename(d) for d in matched_datasets]
    
    # Filter by prefix if provided
    if prefix:
        datasets = [d for d in datasets if d.startswith(prefix)]
    
    return {"datasets": datasets}


@app.post("/api/load_dataset")
def load_dataset(filename: str = "plt00000"):
    """Load a dataset."""
    global current_plotter, current_dataset_name
    
    # Find the full path from matched_datasets
    path = None
    for dataset_path in matched_datasets:
        if os.path.basename(dataset_path) == filename:
            path = dataset_path
            break
    
    # Fallback: try DATA_DIR if no match found
    if path is None and DATA_DIR:
        fallback_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(fallback_path):
            path = fallback_path
    
    if path is None or not os.path.exists(path):
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset not found: {filename}"
        )
    
    try:
        current_plotter = QuokkaPlotter(path, config)
        current_dataset_name = filename
        
        return {
            "message": f"Dataset loaded: {filename}",
            "path": path,
            "domain_dimensions": current_plotter.dataset.domain_dimensions.tolist(),
            "current_time": str(current_plotter.dataset.current_time),
            "max_level": current_plotter.dataset.max_level
        }
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fields")
def get_fields():
    """Get available fields from the loaded dataset."""
    if current_plotter is None:
        raise HTTPException(status_code=400, detail="No dataset loaded")
    
    fields = current_plotter.get_available_fields()
    # Format as list of [namespace, name] for frontend compatibility
    formatted = [[f[0], f[1]] for f in fields]
    return {"fields": formatted}


@app.get("/api/particle_types")
def get_particle_types():
    """Get available particle types."""
    return {
        "particle_types": config.get_particle_types_with_suffix(),
        "default_particle_size": config.default_particle_size
    }


@app.get("/api/slice")
def get_slice(
    axis: str = "z",
    field: str = "density",
    kind: str = "slc",
    weight_field: Optional[str] = None,
    cmap: str = "viridis",
    log_scale: bool = True,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    field_unit: Optional[str] = None,
    dpi: int = 150,
    show_colorbar: bool = False,
    colorbar_label: Optional[str] = None,
    show_scale_bar: bool = False,
    scale_bar_size: Optional[float] = None,
    scale_bar_unit: Optional[str] = None,
    width_value: Optional[float] = None,
    width_unit: Optional[str] = None,
    grids: bool = False,
    timestamp: bool = False,
    top_left_text: Optional[str] = None,
    top_right_text: Optional[str] = None,
    particles: Optional[str] = None,
    particle_size: int = 10,
    particle_color: str = "red",
    camera_theta: float = 45.0,
    camera_phi: float = 45.0,
    n_layers: int = 5,
    preview: bool = True,
    show_box_frame: bool = False,
    # Ignored params for compatibility
    refreshTrigger: Optional[int] = None,
    use_cache: Optional[bool] = None,
):
    """Generate and return a plot image."""
    if current_plotter is None:
        raise HTTPException(status_code=400, detail="No dataset loaded")
    
    try:
        # Build PlotParams
        params = PlotParams(
            cmap=cmap,
            log_scale=log_scale,
            vmin=vmin,
            vmax=vmax,
            field_unit=field_unit,
            dpi=dpi,
            colorbar=ColorbarParams(
                show=show_colorbar,
                label=colorbar_label
            ),
            scale_bar=ScaleBarParams(
                show=show_scale_bar,
                size=scale_bar_size,
                unit=scale_bar_unit
            ),
            width=WidthParams(
                value=width_value,
                unit=width_unit
            ),
            annotations=AnnotationParams(
                show_grids=grids,
                show_timestamp=timestamp,
                top_left_text=top_left_text,
                top_right_text=top_right_text
            ),
            particles=ParticleParams(
                types=[p.strip() for p in particles.split(',')] if particles else [],
                size=particle_size,
                color=particle_color
            ),
            volume=VolumeRenderParams(
                camera_theta=camera_theta,
                camera_phi=camera_phi,
                n_layers=n_layers,
                preview=preview,
                show_box_frame=show_box_frame
            )
        )
        
        # Generate image based on plot type
        if kind == "slc":
            image_bytes = current_plotter.slice(axis, field, params=params)
        elif kind == "prj":
            image_bytes = current_plotter.project(
                axis, field, params=params,
                weight_field=weight_field if weight_field and weight_field != "None" else None
            )
        elif kind == "vol":
            image_bytes = current_plotter.volume(field, params=params)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown plot kind: {kind}")
        
        return Response(content=image_bytes, media_type="image/png")
        
    except Exception as e:
        logger.error(f"Error generating plot: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/current_frame")
def export_current_frame(
    axis: str = "z",
    field: str = "density",
    kind: str = "slc",
    weight_field: Optional[str] = None,
    cmap: str = "viridis",
    log_scale: bool = True,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    dpi: int = 300,
    show_colorbar: bool = False,
    show_scale_bar: bool = False,
    scale_bar_size: Optional[float] = None,
    scale_bar_unit: Optional[str] = None,
    width_value: Optional[float] = None,
    width_unit: Optional[str] = None,
    grids: bool = False,
    timestamp: bool = False,
    particles: Optional[str] = None,
    particle_size: int = 10,
    particle_color: str = "red",
):
    """Export current frame as high-quality PNG."""
    if current_plotter is None:
        raise HTTPException(status_code=400, detail="No dataset loaded")
    
    try:
        params = PlotParams(
            cmap=cmap,
            log_scale=log_scale,
            vmin=vmin,
            vmax=vmax,
            dpi=dpi,
            colorbar=ColorbarParams(show=show_colorbar),
            scale_bar=ScaleBarParams(
                show=show_scale_bar,
                size=scale_bar_size,
                unit=scale_bar_unit
            ),
            width=WidthParams(value=width_value, unit=width_unit),
            annotations=AnnotationParams(show_grids=grids, show_timestamp=timestamp),
            particles=ParticleParams(
                types=[p.strip() for p in particles.split(',')] if particles else [],
                size=particle_size,
                color=particle_color
            )
        )
        
        if kind == "slc":
            image_bytes = current_plotter.slice(axis, field, params=params)
        elif kind == "prj":
            image_bytes = current_plotter.project(axis, field, params=params, weight_field=weight_field)
        else:
            image_bytes = current_plotter.volume(field, params=params)
        
        # Create filename
        sanitized_field = field.replace(":", "_").replace("/", "_")
        filename = f"{current_dataset_name}_{sanitized_field}_{axis}.png"
        
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("YT_STUDIO_HOST", "0.0.0.0")
    port = int(os.environ.get("YT_STUDIO_PORT", "9010"))
    uvicorn.run(app, host=host, port=port)
