"""
Core plotting functionality for plot_quokka.

This module provides the QuokkaPlotter class which is the main interface
for creating visualizations of QUOKKA simulation data.
"""

from typing import Optional, Union, Tuple, Any, List
import os
import tempfile
import numpy as np

# Matplotlib setup - use non-interactive backend
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
matplotlib.rcParams['agg.path.chunksize'] = 10000

import matplotlib.pyplot as plt

# yt imports
try:
    import yt
    from yt.utilities.exceptions import YTCannotParseUnitDisplayName
except ImportError as e:
    raise ImportError("yt is required for plot_quokka") from e

from .dataset import QuokkaDataset
from .params import (
    PlotParams,
    FieldType,
    normalize_field,
    normalize_weight_field,
)
from .config import PlotConfig, DEFAULT_CONFIG


class QuokkaPlotter:
    """
    Main interface for creating QUOKKA visualizations.
    
    This class provides methods for creating slice plots, projection plots,
    and volume renderings of QUOKKA simulation data.
    
    Parameters
    ----------
    dataset : str or QuokkaDataset
        Path to dataset or a QuokkaDataset object.
    config : PlotConfig, optional
        Configuration settings. Uses defaults if not provided.
    
    Examples
    --------
    Basic usage:
    >>> plotter = QuokkaPlotter("data/plt00020")
    >>> plotter.slice("z", "density", output="density_slice.png")
    
    With parameters:
    >>> from plot_quokka import PlotParams, ColorbarParams
    >>> params = PlotParams(
    ...     cmap="inferno",
    ...     log_scale=True,
    ...     colorbar=ColorbarParams(show=True)
    ... )
    >>> plotter.slice("z", "density", params=params)
    
    Projection plot:
    >>> plotter.project("z", "density", weight_field="density")
    
    Volume rendering:
    >>> plotter.volume("density", camera_theta=45, camera_phi=30)
    """
    
    def __init__(
        self,
        dataset: Union[str, QuokkaDataset],
        config: Optional[PlotConfig] = None,
    ):
        # Handle dataset input
        if isinstance(dataset, str):
            self._dataset = QuokkaDataset(dataset)
        elif isinstance(dataset, QuokkaDataset):
            self._dataset = dataset
        else:
            raise TypeError(f"Expected str or QuokkaDataset, got {type(dataset)}")
        
        # Configuration
        self._config = config or DEFAULT_CONFIG
    
    @property
    def dataset(self) -> QuokkaDataset:
        """Get the dataset object."""
        return self._dataset
    
    @property
    def config(self) -> PlotConfig:
        """Get the configuration object."""
        return self._config
    
    @property
    def ds(self) -> Any:
        """Get the underlying yt dataset."""
        return self._dataset.ds
    
    def slice(
        self,
        axis: str,
        field: FieldType,
        params: Optional[PlotParams] = None,
        coord: Optional[float] = None,
        output: Optional[str] = None,
    ) -> Union[bytes, str]:
        """
        Create a slice plot.
        
        Parameters
        ----------
        axis : str
            Axis perpendicular to slice ('x', 'y', or 'z').
        field : str or tuple
            Field to plot (e.g., 'density' or ('gas', 'density')).
        params : PlotParams, optional
            Plot parameters. Uses defaults if not provided.
        coord : float, optional
            Slice coordinate. Uses domain center if not provided.
        output : str, optional
            Output file path. If None, returns image bytes.
        
        Returns
        -------
        bytes or str
            Image bytes if output is None, otherwise output file path.
        
        Examples
        --------
        >>> plotter.slice("z", "density")  # Returns bytes
        >>> plotter.slice("z", "density", output="slice.png")  # Saves to file
        """
        return self._create_plot("slc", axis, field, params, coord, output=output)
    
    def project(
        self,
        axis: str,
        field: FieldType,
        params: Optional[PlotParams] = None,
        weight_field: Optional[FieldType] = None,
        output: Optional[str] = None,
    ) -> Union[bytes, str]:
        """
        Create a projection plot.
        
        Parameters
        ----------
        axis : str
            Axis along which to project ('x', 'y', or 'z').
        field : str or tuple
            Field to plot.
        params : PlotParams, optional
            Plot parameters.
        weight_field : str or tuple, optional
            Weight field for weighted projection.
        output : str, optional
            Output file path.
        
        Returns
        -------
        bytes or str
            Image bytes if output is None, otherwise output file path.
        """
        return self._create_plot(
            "prj", axis, field, params=params,
            weight_field=weight_field, output=output
        )
    
    def volume(
        self,
        field: FieldType,
        params: Optional[PlotParams] = None,
        output: Optional[str] = None,
    ) -> Union[bytes, str]:
        """
        Create a volume rendering.
        
        Parameters
        ----------
        field : str or tuple
            Field to render.
        params : PlotParams, optional
            Plot parameters (uses params.volume for volume-specific settings).
        output : str, optional
            Output file path.
        
        Returns
        -------
        bytes or str
            Image bytes if output is None, otherwise output file path.
        """
        return self._create_plot("vol", "z", field, params=params, output=output)
    
    def _create_plot(
        self,
        kind: str,
        axis: str,
        field: FieldType,
        params: Optional[PlotParams] = None,
        coord: Optional[float] = None,
        weight_field: Optional[FieldType] = None,
        output: Optional[str] = None,
    ) -> Union[bytes, str]:
        """Internal method to create plots."""
        # Use default params if not provided
        params = params or PlotParams()
        
        # Normalize field
        field_tuple = normalize_field(field)
        
        # Get coordinate if not provided
        if coord is None and kind != "vol":
            coord = self._dataset.get_center_coordinate(axis)
        
        # Handle weight field for projections
        weight = None
        if kind == "prj":
            weight = normalize_weight_field(weight_field)
        
        # Route to appropriate rendering method
        if kind == "vol":
            image_bytes = self._render_volume(field_tuple, params)
        else:
            image_bytes = self._render_2d(kind, axis, field_tuple, params, coord, weight)
        
        # Handle output
        if output is not None:
            with open(output, 'wb') as f:
                f.write(image_bytes)
            return output
        
        return image_bytes
    
    def _render_2d(
        self,
        kind: str,
        axis: str,
        field_tuple: Tuple[str, str],
        params: PlotParams,
        coord: float,
        weight: Optional[Tuple[str, str]],
    ) -> bytes:
        """Render a 2D slice or projection plot."""
        ds = self.ds
        
        # Create plot object
        if kind == "slc":
            plot = yt.SlicePlot(ds, axis, field_tuple, center=ds.domain_center)
        elif kind == "prj":
            plot = yt.ProjectionPlot(
                ds, axis, field_tuple, 
                weight_field=weight, 
                center=ds.domain_center
            )
        else:
            raise ValueError(f"Unknown plot kind: {kind}")
        
        # Apply configuration
        self._configure_2d_plot(plot, field_tuple, axis, params)
        
        # Save to temporary file and read bytes
        return self._plot_to_bytes(plot, params.dpi)
    
    def _configure_2d_plot(
        self,
        plot: Any,
        field_tuple: Tuple[str, str],
        axis: str,
        params: PlotParams,
    ) -> None:
        """Apply configuration to a 2D plot."""
        # Set units if specified
        if params.field_unit:
            try:
                plot.set_unit(field_tuple, params.field_unit)
            except Exception:
                pass  # Silently ignore unit errors
        
        # Core settings
        plot.set_cmap(field_tuple, params.cmap)
        plot.set_log(field_tuple, params.log_scale)
        plot.set_background_color(field_tuple, params.background_color)
        
        # Set width if specified
        is_squared = False
        width_tuple = params.width.to_tuple()
        if width_tuple:
            plot.set_width(width_tuple)
            is_squared = True
        
        # Colorbar
        if params.colorbar.show and params.colorbar.label:
            plot.set_colorbar_label(field_tuple, params.colorbar.label)
        
        # Color limits
        if params.vmin is not None and params.vmax is not None:
            plot.set_zlim(field_tuple, params.vmin, params.vmax)
        elif params.vmin is not None:
            plot.set_zlim(field_tuple, params.vmin, 'max')
        elif params.vmax is not None:
            plot.set_zlim(field_tuple, 'min', params.vmax)
        
        # Annotations
        self._add_annotations(plot, axis, params)
        
        # Figure sizing
        self._configure_figure_size(plot, axis, params, is_squared)
        
        # Visibility
        if not params.show_axes:
            plot.hide_axes(draw_frame=True)
        
        if not params.colorbar.show:
            plot.hide_colorbar()
    
    def _add_annotations(
        self,
        plot: Any,
        axis: str,
        params: PlotParams,
    ) -> None:
        """Add annotations to the plot."""
        ds = self.ds
        
        # Particles
        if params.particles.types:
            if 'particles' in ds.parameters:
                ad = ds.all_data()
                Lx = ds.domain_right_edge[0] - ds.domain_left_edge[0]
                
                for p_type in params.particles.types:
                    if p_type not in ds.parameters.get('particle_info', {}):
                        continue
                    
                    num_particles = ds['particle_info'][p_type]['num_particles']
                    if num_particles == 0:
                        continue
                    
                    try:
                        pos = ad[(p_type, "particle_position_x")]
                        if len(pos) > 0:
                            plot.annotate_particles(
                                Lx * params.particles.depth_fraction,
                                p_size=params.particles.size,
                                col=params.particles.color,
                                marker=params.particles.marker,
                                ptype=p_type
                            )
                    except Exception:
                        continue
        
        # Grid boundaries
        if params.annotations.show_grids:
            plot.annotate_grids(edgecolors='white', linewidth=1)
        
        # Timestamp
        if params.annotations.show_timestamp:
            plot.annotate_timestamp(corner='upper_left')
        
        # Scale bar
        axis_info = self._dataset.get_axis_info(axis)
        aspect = axis_info["y_width"] / axis_info["x_width"]
        scale_bar_x_loc = 0.5 if aspect > 1.3 else 0.15
        scale_bar_y_loc = 0.15 if aspect < 1/1.3 else 0.1
        scale_bar_pos = (scale_bar_x_loc, scale_bar_y_loc)
        
        if params.scale_bar.size and params.scale_bar.unit:
            plot.annotate_scale(
                coeff=params.scale_bar.size,
                unit=params.scale_bar.unit,
                pos=scale_bar_pos,
                coord_system='axis',
                min_frac=0.05,
                max_frac=0.16,
                size_bar_args={'pad': 0.55, 'sep': 8, 'borderpad': 5, 'color': 'w'}
            )
        elif params.scale_bar.show:
            plot.annotate_scale(
                pos=scale_bar_pos,
                coord_system='axis',
                min_frac=0.05,
                max_frac=0.16,
                size_bar_args={'pad': 0.55, 'sep': 8, 'borderpad': 5, 'color': 'w'}
            )
        
        # Text annotations
        if params.annotations.top_left_text:
            plot.annotate_text(
                (0.02, 0.98),
                params.annotations.top_left_text,
                coord_system='axis',
                text_args={
                    'color': 'white',
                    'verticalalignment': 'top',
                    'horizontalalignment': 'left'
                }
            )
        
        if params.annotations.top_right_text:
            plot.annotate_text(
                (0.98, 0.98),
                params.annotations.top_right_text,
                coord_system='axis',
                text_args={
                    'color': 'white',
                    'verticalalignment': 'top',
                    'horizontalalignment': 'right'
                }
            )
    
    def _configure_figure_size(
        self,
        plot: Any,
        axis: str,
        params: PlotParams,
        is_squared: bool,
    ) -> None:
        """Configure figure size based on aspect ratio."""
        axis_info = self._dataset.get_axis_info(axis)
        aspect = axis_info["y_width"] / axis_info["x_width"]
        real_aspect = aspect if not is_squared else 1.0
        
        short_size = params.short_size or self._config.short_size
        
        is_close_to_square = 3.0 / 4.1 < aspect < 4.1 / 3
        is_make_bigger = is_close_to_square
        
        if not is_squared:
            if aspect > 1:
                fig_size = short_size * aspect
                fig_size = fig_size * 1.5 if is_make_bigger else fig_size
            else:
                fig_size = short_size / aspect
                fig_size = fig_size * 1.5 if is_make_bigger else fig_size
        else:
            fig_size = short_size * 1.5
        
        plot.set_figure_size(fig_size)
        plot.set_font_size(params.font_size or self._config.font_size)
    
    def _render_volume(
        self,
        field_tuple: Tuple[str, str],
        params: PlotParams,
    ) -> bytes:
        """Render a volume visualization."""
        ds = self.ds
        vol_params = params.volume
        
        # Create scene
        sc = yt.create_scene(ds, field=field_tuple)
        source = sc[0]
        
        # Get data bounds
        data_bounds = ds.all_data().quantities.extrema(field_tuple)
        t_min = float(params.vmin) if params.vmin is not None else float(data_bounds[0])
        t_max = float(params.vmax) if params.vmax is not None else float(data_bounds[1])
        bounds = [t_min, t_max]
        
        # Set up transfer function
        if params.log_scale:
            real_bounds = [np.log10(t_min), np.log10(t_max)]
        else:
            real_bounds = bounds
        
        tf = yt.ColorTransferFunction(real_bounds, grey_opacity=vol_params.grey_opacity)
        tf.add_layers(vol_params.n_layers, colormap=params.cmap)
        
        source.tfh.tf = tf
        source.tfh.bounds = bounds
        source.tfh.set_log(params.log_scale)
        
        # Camera setup
        use_perspective = vol_params.use_perspective
        if self._config.use_perspective_camera is not None:
            use_perspective = self._config.use_perspective_camera
        
        if use_perspective:
            cam = sc.add_camera(ds, lens_type="perspective")
        else:
            cam = sc.camera
        
        # Resolution
        short_size = params.short_size or self._config.short_size
        dpi = params.dpi or self._config.default_dpi
        
        if vol_params.preview:
            res_px = 512
        else:
            res_px = int(short_size * dpi * 2.0)
        cam.resolution = (res_px, res_px)
        
        # Camera direction from spherical coordinates
        theta_rad = np.radians(vol_params.camera_theta)
        phi_rad = np.radians(vol_params.camera_phi)
        
        cx = np.sin(theta_rad) * np.cos(phi_rad)
        cy = np.sin(theta_rad) * np.sin(phi_rad)
        cz = np.cos(theta_rad)
        
        view_dir = np.array([cx, cy, cz], dtype=float)
        norm = np.linalg.norm(view_dir)
        view_dir = view_dir / norm if norm > 0 else np.array([1.0, 0.0, 0.0])
        
        # North vector
        if abs(view_dir[2]) > 0.9:
            north = np.array([0, 1, 0])
        else:
            north = np.array([0, 0, 1])
        
        # Width
        width_tuple = params.width.to_tuple()
        if width_tuple:
            cam.set_width(width_tuple)
        else:
            # Smart width based on viewing direction
            domain_width = ds.domain_width
            max_dim_idx = np.argmax(domain_width)
            max_width = domain_width[max_dim_idx]
            
            if abs(view_dir[max_dim_idx]) > 0.9:
                min_width = np.min(domain_width)
                cam.set_width(min_width)
            else:
                cam.set_width(max_width)
        
        # Position and orientation
        cam.set_focus(ds.domain_center)
        cam.switch_orientation(normal_vector=view_dir, north_vector=north)
        
        if use_perspective:
            current_width = cam.width
            distance = 1.5 * current_width
            offset = view_dir * distance
            cam.position = ds.domain_center - offset
        
        # Add box frame if requested
        if vol_params.show_box_frame:
            from yt.visualization.volume_rendering.api import BoxSource
            box_source = BoxSource(
                ds.domain_left_edge,
                ds.domain_right_edge,
                color=[0.2, 0.2, 0.2, 0.1]
            )
            sc.add_source(box_source)
        
        # Render to bytes
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            sc.save(tmp_path, sigma_clip=3.5)
            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _plot_to_bytes(self, plot: Any, dpi: int) -> bytes:
        """Convert a yt plot to PNG bytes."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            plot.save(
                tmp_path,
                mpl_kwargs={"dpi": dpi, "bbox_inches": "tight", "pad_inches": 0.05}
            )
            with open(tmp_path, 'rb') as f:
                return f.read()
        except YTCannotParseUnitDisplayName:
            # Retry with simplified label
            for field_key in plot.plots:
                plot.set_colorbar_label(field_key, str(field_key[1]))
            plot.save(
                tmp_path,
                mpl_kwargs={"dpi": dpi, "bbox_inches": "tight", "pad_inches": 0.05}
            )
            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def get_available_fields(self) -> List[Tuple[str, str]]:
        """Get list of available fields."""
        return self._dataset.fields
    
    def get_field_info(self, field: FieldType) -> dict:
        """Get information about a field."""
        field_tuple = normalize_field(field)
        extrema = self._dataset.get_field_extrema(field_tuple)
        return {
            "field": field_tuple,
            "min": float(extrema[0]),
            "max": float(extrema[1]),
        }
    
    def __repr__(self) -> str:
        return f"QuokkaPlotter(dataset={self._dataset.path})"
