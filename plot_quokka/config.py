"""
Configuration module for plot_quokka.

Handles loading and managing plot configuration from YAML files
or programmatic settings.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import os
import yaml


@dataclass
class PlotConfig:
    """Configuration settings for QUOKKA visualization plots.
    
    This class holds global configuration settings that apply to all plots
    unless overridden by specific PlotParams.
    
    Attributes
    ----------
    short_size : float
        The size of the short dimension of the figure in inches.
    font_size : int
        Default font size for labels and annotations.
    scale_bar_height_fraction : float
        Height of the scale bar as a fraction of the plot.
    colormap_fraction : float
        Width of the colormap as a fraction of the plot width.
    default_dpi : int
        Default DPI for output images.
    cache_max_size : int
        Maximum number of cached plot images.
    show_axes : bool
        Whether to show axes by default.
    use_perspective_camera : bool
        Whether to use perspective camera for volume rendering.
    particle_types : List[str]
        List of supported particle types.
    default_particle_size : int
        Default marker size for particles.
    """
    
    # Figure sizing
    short_size: float = 3.6
    font_size: int = 20
    
    # Scale bar settings
    scale_bar_height_fraction: float = 15.0
    
    # Colormap settings
    colormap_fraction: float = 0.1
    
    # Output settings
    default_dpi: int = 300
    
    # Cache settings
    cache_max_size: int = 32
    
    # Display options
    show_axes: bool = False
    
    # 3D rendering options
    use_perspective_camera: bool = True
    
    # Particle settings
    particle_types: List[str] = field(default_factory=lambda: [
        "Rad", "CIC", "CICRad", "StochasticStellarPop", "Sink"
    ])
    default_particle_size: int = 10
    
    def get_particle_types_with_suffix(self) -> List[str]:
        """Return particle types with '_particles' suffix."""
        return [f"{ptype}_particles" for ptype in self.particle_types]

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "short_size": self.short_size,
            "font_size": self.font_size,
            "scale_bar_height_fraction": self.scale_bar_height_fraction,
            "colormap_fraction": self.colormap_fraction,
            "default_dpi": self.default_dpi,
            "cache_max_size": self.cache_max_size,
            "show_axes": self.show_axes,
            "use_perspective_camera": self.use_perspective_camera,
            "particle_types": self.particle_types,
            "default_particle_size": self.default_particle_size,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlotConfig":
        """Create configuration from dictionary."""
        config = cls()
        if "short_size" in data:
            config.short_size = float(data["short_size"])
        if "font_size" in data:
            config.font_size = int(data["font_size"])
        if "scale_bar_height_fraction" in data:
            config.scale_bar_height_fraction = float(data["scale_bar_height_fraction"])
        if "colormap_fraction" in data:
            config.colormap_fraction = float(data["colormap_fraction"])
        if "default_dpi" in data:
            config.default_dpi = int(data["default_dpi"])
        if "cache_max_size" in data:
            config.cache_max_size = int(data["cache_max_size"])
        if "show_axes" in data:
            config.show_axes = bool(data["show_axes"])
        if "use_perspective_camera" in data:
            config.use_perspective_camera = bool(data["use_perspective_camera"])
        if "particle_types" in data:
            config.particle_types = list(data["particle_types"])
        if "default_particle_size" in data:
            config.default_particle_size = int(data["default_particle_size"])
        return config


def load_config(config_path: Optional[str] = None) -> PlotConfig:
    """
    Load configuration from a YAML file.
    
    Parameters
    ----------
    config_path : str, optional
        Path to the configuration YAML file. If None, returns default config.
    
    Returns
    -------
    PlotConfig
        Configuration object with loaded settings.
    
    Examples
    --------
    >>> config = load_config("config.yaml")
    >>> config.default_dpi
    300
    >>> config.font_size = 24  # Override setting
    """
    config = PlotConfig()
    
    if config_path is None:
        return config
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f)
        
        if yaml_config:
            config = PlotConfig.from_dict(yaml_config)
    
    return config


def save_config(config: PlotConfig, config_path: str) -> None:
    """
    Save configuration to a YAML file.
    
    Parameters
    ----------
    config : PlotConfig
        Configuration object to save.
    config_path : str
        Path to save the configuration file.
    """
    with open(config_path, "w") as f:
        yaml.safe_dump(config.to_dict(), f, default_flow_style=False)


# Default configuration instance
DEFAULT_CONFIG = PlotConfig()
