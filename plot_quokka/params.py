"""
Parameter classes for plot_quokka.

This module defines dataclasses for all plot parameters, providing
a clean, type-safe interface for configuring visualizations.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Union


@dataclass
class ColorbarParams:
    """Parameters for colorbar configuration.
    
    Attributes
    ----------
    show : bool
        Whether to show the colorbar.
    label : Optional[str]
        Custom label for the colorbar. If None, uses default field label.
    orientation : str
        Orientation of the colorbar: 'right', 'left', 'top', 'bottom'.
    """
    show: bool = True
    label: Optional[str] = None
    orientation: str = "right"


@dataclass
class ScaleBarParams:
    """Parameters for scale bar configuration.
    
    Attributes
    ----------
    show : bool
        Whether to show the scale bar.
    size : Optional[float]
        Size of the scale bar in the specified unit. If None, auto-calculated.
    unit : Optional[str]
        Unit for the scale bar (e.g., 'pc', 'kpc', 'AU').
    position : Tuple[float, float]
        Position of the scale bar in axis coordinates (0-1).
    color : str
        Color of the scale bar.
    """
    show: bool = False
    size: Optional[float] = None
    unit: Optional[str] = None
    position: Tuple[float, float] = (0.5, 0.15)
    color: str = "white"


@dataclass
class WidthParams:
    """Parameters for plot width/zoom configuration.
    
    Attributes
    ----------
    value : Optional[float]
        Width value. If None, uses full domain width.
    unit : Optional[str]
        Unit for the width (e.g., 'pc', 'kpc', 'code_length').
    """
    value: Optional[float] = None
    unit: Optional[str] = None
    
    def to_tuple(self) -> Optional[Tuple[float, str]]:
        """Convert to tuple format used by yt."""
        if self.value is not None and self.unit is not None:
            return (self.value, self.unit)
        return None


@dataclass
class ParticleParams:
    """Parameters for particle overlay configuration.
    
    Attributes
    ----------
    types : List[str]
        List of particle types to display (e.g., ['CIC_particles']).
    size : int
        Marker size for particles.
    color : str
        Color of particle markers.
    marker : str
        Marker style (matplotlib marker).
    depth_fraction : float
        Depth fraction of box size for particle selection.
    """
    types: List[str] = field(default_factory=list)
    size: int = 10
    color: str = "red"
    marker: str = "o"
    depth_fraction: float = 0.1


@dataclass
class AnnotationParams:
    """Parameters for text annotations.
    
    Attributes
    ----------
    show_timestamp : bool
        Whether to show simulation timestamp.
    show_grids : bool
        Whether to show AMR grid boundaries.
    top_left_text : Optional[str]
        Text to display in top-left corner.
    top_right_text : Optional[str]
        Text to display in top-right corner.
    """
    show_timestamp: bool = False
    show_grids: bool = False
    top_left_text: Optional[str] = None
    top_right_text: Optional[str] = None


@dataclass
class VolumeRenderParams:
    """Parameters for volume rendering.
    
    Attributes
    ----------
    camera_theta : float
        Polar angle of camera in degrees (0-180).
    camera_phi : float
        Azimuthal angle of camera in degrees (0-360).
    n_layers : int
        Number of transfer function layers.
    alpha_min : float
        Minimum alpha (opacity) value.
    alpha_max : float
        Maximum alpha (opacity) value.
    grey_opacity : bool
        Whether to use grey opacity mode.
    show_box_frame : bool
        Whether to show the domain bounding box.
    use_perspective : bool
        Whether to use perspective camera (vs orthographic).
    preview : bool
        If True, use lower resolution for faster preview.
    """
    camera_theta: float = 45.0
    camera_phi: float = 45.0
    n_layers: int = 5
    alpha_min: float = 0.1
    alpha_max: float = 1.0
    grey_opacity: bool = False
    show_box_frame: bool = False
    use_perspective: bool = True
    preview: bool = False


@dataclass
class PlotParams:
    """Main parameters class for all plot types.
    
    This class aggregates all plot parameters and provides defaults
    suitable for most visualizations.
    
    Attributes
    ----------
    cmap : str
        Matplotlib colormap name.
    log_scale : bool
        Whether to use logarithmic scale for the field.
    vmin : Optional[float]
        Minimum value for color scale.
    vmax : Optional[float]
        Maximum value for color scale.
    field_unit : Optional[str]
        Unit to display for the field.
    dpi : int
        Resolution of output image in dots per inch.
    short_size : float
        Size of the short dimension of the figure in inches.
    font_size : int
        Font size for labels and annotations.
    show_axes : bool
        Whether to show axes with labels.
    background_color : str
        Background color of the plot.
    colorbar : ColorbarParams
        Colorbar configuration.
    scale_bar : ScaleBarParams
        Scale bar configuration.
    width : WidthParams
        Plot width/zoom configuration.
    particles : ParticleParams
        Particle overlay configuration.
    annotations : AnnotationParams
        Text annotation configuration.
    volume : VolumeRenderParams
        Volume rendering configuration.
    
    Examples
    --------
    >>> params = PlotParams(cmap="inferno", log_scale=True, vmin=1e-20)
    >>> params.colorbar.show = True
    >>> params.colorbar.label = "Density (g/cm³)"
    
    >>> # Using nested params
    >>> params = PlotParams(
    ...     colorbar=ColorbarParams(show=True, label="Temperature"),
    ...     scale_bar=ScaleBarParams(show=True, size=10, unit="pc")
    ... )
    """
    # Core plotting parameters
    cmap: str = "viridis"
    log_scale: bool = True
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    field_unit: Optional[str] = None
    
    # Figure parameters
    dpi: int = 300
    short_size: float = 3.6
    font_size: int = 20
    show_axes: bool = False
    background_color: str = "black"
    
    # Nested parameter groups
    colorbar: ColorbarParams = field(default_factory=ColorbarParams)
    scale_bar: ScaleBarParams = field(default_factory=ScaleBarParams)
    width: WidthParams = field(default_factory=WidthParams)
    particles: ParticleParams = field(default_factory=ParticleParams)
    annotations: AnnotationParams = field(default_factory=AnnotationParams)
    volume: VolumeRenderParams = field(default_factory=VolumeRenderParams)

    def with_colorbar(self, show: bool = True, label: Optional[str] = None, 
                      orientation: str = "right") -> "PlotParams":
        """Return a copy with updated colorbar settings."""
        import copy
        new_params = copy.deepcopy(self)
        new_params.colorbar = ColorbarParams(show=show, label=label, orientation=orientation)
        return new_params

    def with_scale_bar(self, show: bool = True, size: Optional[float] = None,
                       unit: Optional[str] = None) -> "PlotParams":
        """Return a copy with updated scale bar settings."""
        import copy
        new_params = copy.deepcopy(self)
        new_params.scale_bar = ScaleBarParams(show=show, size=size, unit=unit)
        return new_params

    def with_width(self, value: float, unit: str) -> "PlotParams":
        """Return a copy with updated width settings."""
        import copy
        new_params = copy.deepcopy(self)
        new_params.width = WidthParams(value=value, unit=unit)
        return new_params


# Type alias for field specification
FieldType = Union[str, Tuple[str, str]]


def normalize_field(field_input: FieldType) -> Tuple[str, str]:
    """
    Normalize field input to a (namespace, name) tuple.
    
    Parameters
    ----------
    field_input : str or tuple
        Field specification. Can be:
        - A string like "density" (assumes "gas" namespace)
        - A string like "gas:density" (explicit namespace)
        - A tuple like ("gas", "density")
    
    Returns
    -------
    Tuple[str, str]
        Normalized (namespace, name) tuple.
    
    Raises
    ------
    ValueError
        If the field input cannot be parsed.
    
    Examples
    --------
    >>> normalize_field("density")
    ('gas', 'density')
    >>> normalize_field("gas:temperature")
    ('gas', 'temperature')
    >>> normalize_field(("index", "cell_volume"))
    ('index', 'cell_volume')
    """
    if isinstance(field_input, tuple):
        if len(field_input) < 2:
            raise ValueError("Field tuple must have at least two elements")
        return (str(field_input[0]).strip(), str(field_input[1]).strip())
    
    if isinstance(field_input, list):
        if len(field_input) < 2:
            raise ValueError("Field list must have at least two elements")
        return (str(field_input[0]).strip(), str(field_input[1]).strip())
    
    if isinstance(field_input, str):
        raw = field_input.strip()
        if ':' in raw:
            namespace, name = raw.split(':', 1)
            return (namespace.strip(), name.strip())
        return ("gas", raw)
    
    raise ValueError(f"Cannot interpret field input: {type(field_input)}")


def normalize_weight_field(weight_field: Optional[Union[str, Tuple[str, str]]]) -> Optional[Tuple[str, str]]:
    """
    Normalize weight field input for projections.
    
    Parameters
    ----------
    weight_field : str, tuple, or None
        Weight field specification. Common values:
        - None or "None": No weight field
        - "density": Use gas density
        - "cell_volume": Use cell volume
        - Custom field tuple
    
    Returns
    -------
    Optional[Tuple[str, str]]
        Normalized weight field tuple, or None if no weighting.
    
    Examples
    --------
    >>> normalize_weight_field(None)
    None
    >>> normalize_weight_field("density")
    ('gas', 'density')
    >>> normalize_weight_field("cell_volume")
    ('index', 'cell_volume')
    """
    if weight_field is None or weight_field == "None":
        return None
    
    # Handle common shortcuts
    shortcuts = {
        "density": ("gas", "density"),
        "cell_volume": ("index", "cell_volume"),
        "cell_mass": ("gas", "cell_mass"),
    }
    
    if isinstance(weight_field, str) and weight_field in shortcuts:
        return shortcuts[weight_field]
    
    try:
        return normalize_field(weight_field)
    except ValueError:
        return ("gas", str(weight_field))
