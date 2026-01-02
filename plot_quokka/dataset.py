"""
Dataset handling for plot_quokka.

This module provides the QuokkaDataset class for loading and managing
QUOKKA simulation data, including adding derived fields.
"""

from typing import Optional, List, Tuple, Any, Dict
import os
import numpy as np

# Import yt with error handling
try:
    import yt
    import unyt
except ImportError as e:
    raise ImportError(
        "yt and unyt are required for plot_quokka. "
        "Install with: pip install yt unyt"
    ) from e


class QuokkaDataset:
    """
    Wrapper class for QUOKKA simulation datasets.
    
    This class handles loading yt datasets and adding derived fields
    specific to QUOKKA simulations.
    
    Parameters
    ----------
    path : str
        Path to the QUOKKA dataset (e.g., 'plt00500').
    add_derived_fields : bool, optional
        Whether to automatically add derived fields on load (default: True).
    gamma : float, optional
        Adiabatic index for thermodynamic calculations (default: 5/3).
    mean_molecular_weight : float, optional
        Mean molecular weight in atomic mass units (default: 1.0).
    
    Attributes
    ----------
    ds : yt.Dataset
        The underlying yt dataset object.
    path : str
        Path to the loaded dataset.
    
    Examples
    --------
    >>> dataset = QuokkaDataset("data/plt00020")
    >>> print(dataset.domain_dimensions)
    [64, 64, 64]
    >>> print(dataset.fields)
    [('gas', 'density'), ('gas', 'velocity_x'), ...]
    """
    
    def __init__(
        self,
        path: str,
        add_derived_fields: bool = True,
        gamma: float = 5.0 / 3.0,
        mean_molecular_weight: float = 1.0,
    ):
        self.path = os.path.abspath(path)
        self.gamma = gamma
        self.mean_molecular_weight = mean_molecular_weight
        self._ds: Optional[Any] = None
        
        # Load the dataset
        self._load()
        
        # Add derived fields if requested
        if add_derived_fields:
            self._add_derived_fields()
    
    def _load(self) -> None:
        """Load the dataset using yt."""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Dataset not found: {self.path}")
        
        # Suppress yt's verbose output
        yt.set_log_level(40)  # 40 = Error only
        
        self._ds = yt.load(self.path)
    
    @property
    def ds(self) -> Any:
        """Get the underlying yt dataset object."""
        if self._ds is None:
            raise RuntimeError("Dataset not loaded")
        return self._ds
    
    @property
    def domain_dimensions(self) -> np.ndarray:
        """Get domain dimensions."""
        return self.ds.domain_dimensions
    
    @property
    def domain_width(self) -> Any:
        """Get domain width."""
        return self.ds.domain_width
    
    @property
    def domain_center(self) -> Any:
        """Get domain center."""
        return self.ds.domain_center
    
    @property
    def domain_left_edge(self) -> Any:
        """Get domain left edge."""
        return self.ds.domain_left_edge
    
    @property
    def domain_right_edge(self) -> Any:
        """Get domain right edge."""
        return self.ds.domain_right_edge
    
    @property
    def current_time(self) -> Any:
        """Get current simulation time."""
        return self.ds.current_time
    
    @property
    def max_level(self) -> int:
        """Get maximum AMR refinement level."""
        return self.ds.max_level
    
    @property
    def fields(self) -> List[Tuple[str, str]]:
        """Get list of available fields (both native and derived)."""
        combined = list(self.ds.field_list) + list(self.ds.derived_field_list)
        unique = []
        seen = set()
        
        for field_entry in combined:
            if not isinstance(field_entry, (tuple, list)) or len(field_entry) < 2:
                continue
            namespace = str(field_entry[0]).strip()
            name = str(field_entry[1]).strip()
            key = (namespace, name)
            if key not in seen:
                seen.add(key)
                unique.append(key)
        
        return unique
    
    @property
    def particle_types(self) -> List[str]:
        """Get list of available particle types."""
        if 'particles' not in self.ds.parameters:
            return []
        
        particle_info = self.ds.parameters.get('particle_info', {})
        return list(particle_info.keys())
    
    def has_field(self, field: Tuple[str, str]) -> bool:
        """Check if a field exists in the dataset."""
        return field in self.fields
    
    def get_field_extrema(self, field: Tuple[str, str]) -> Tuple[float, float]:
        """Get the minimum and maximum values of a field."""
        ad = self.ds.all_data()
        return ad.quantities.extrema(field)
    
    def all_data(self) -> Any:
        """Get an all_data container for the dataset."""
        return self.ds.all_data()
    
    def _add_derived_fields(self) -> None:
        """Add derived fields to the dataset."""
        # Physical constants
        m_u = 1.660539e-24 * unyt.g
        k_B = unyt.physical_constants.boltzmann_constant
        mean_molecular_weight_per_H = self.mean_molecular_weight * m_u
        gamma = self.gamma
        
        ds = self.ds
        
        # Number Density
        if ("gas", "number_density") not in ds.derived_field_list:
            def _number_density(field, data):
                return data[("gas", "density")] / mean_molecular_weight_per_H
            try:
                ds.add_field(
                    ("gas", "number_density"),
                    function=_number_density,
                    units="auto",
                    sampling_type="cell",
                    force_override=True,
                    display_name="Number Density"
                )
            except Exception:
                pass  # Silently skip if field cannot be added
        
        # Temperature
        if ("gas", "temperature") not in ds.derived_field_list:
            self._add_temperature_field(ds, gamma, mean_molecular_weight_per_H, k_B)
        
        # Velocity Magnitude
        if ("gas", "velocity_magnitude") not in ds.derived_field_list:
            def _velocity_magnitude(field, data):
                return np.sqrt(
                    data[("gas", "velocity_x")]**2 +
                    data[("gas", "velocity_y")]**2 +
                    data[("gas", "velocity_z")]**2
                )
            try:
                ds.add_field(
                    ("gas", "velocity_magnitude"),
                    function=_velocity_magnitude,
                    units="auto",
                    sampling_type="cell",
                    force_override=True,
                    display_name="Velocity Magnitude"
                )
            except Exception:
                pass
    
    def _add_temperature_field(self, ds: Any, gamma: float, 
                                mean_molecular_weight_per_H: Any, k_B: Any) -> None:
        """Add temperature field based on available energy fields."""
        # Check for total_energy_density
        has_total_energy = (
            ("gas", "total_energy_density") in ds.field_list or
            ("gas", "total_energy_density") in ds.derived_field_list
        )
        
        if has_total_energy:
            def _temperature_derived(field, data):
                etot = data[("gas", "total_energy_density")]
                density = data[("gas", "density")]
                kinetic_energy = 0.5 * density * (
                    data[("gas", "velocity_x")]**2 +
                    data[("gas", "velocity_y")]**2 +
                    data[("gas", "velocity_z")]**2
                )
                eint = etot - kinetic_energy
                return eint * (gamma - 1.0) / (density / mean_molecular_weight_per_H * k_B)
            
            try:
                ds.add_field(
                    ("gas", "temperature"),
                    function=_temperature_derived,
                    units="auto",
                    sampling_type="cell",
                    force_override=True,
                    display_name="Temperature"
                )
                return
            except Exception:
                pass
        
        # Fall back to internal_energy_density
        has_internal_energy = (
            ("gas", "internal_energy_density") in ds.field_list or
            ("gas", "internal_energy_density") in ds.derived_field_list
        )
        
        if has_internal_energy:
            def _temperature_from_internal(field, data):
                eint = data[("gas", "internal_energy_density")]
                density = data[("gas", "density")]
                return eint * (gamma - 1.0) / (density / mean_molecular_weight_per_H * k_B)
            
            try:
                ds.add_field(
                    ("gas", "temperature"),
                    function=_temperature_from_internal,
                    units="auto",
                    sampling_type="cell",
                    force_override=True,
                    display_name="Temperature"
                )
            except Exception:
                pass
    
    def get_axis_info(self, axis: str) -> Dict[str, Any]:
        """
        Get axis information for plotting.
        
        Parameters
        ----------
        axis : str
            Axis name ('x', 'y', or 'z').
        
        Returns
        -------
        dict
            Dictionary containing axis_id, x_axis_id, y_axis_id,
            and the corresponding widths.
        """
        ds = self.ds
        axis_id = ds.coordinates.axis_id[axis]
        x_ax_id = ds.coordinates.x_axis[axis_id]
        y_ax_id = ds.coordinates.y_axis[axis_id]
        
        return {
            "axis_id": axis_id,
            "x_axis_id": x_ax_id,
            "y_axis_id": y_ax_id,
            "x_width": float(ds.domain_width[x_ax_id].v),
            "y_width": float(ds.domain_width[y_ax_id].v),
        }
    
    def get_center_coordinate(self, axis: str) -> float:
        """Get the domain center coordinate along an axis."""
        axis_id = self.ds.coordinates.axis_id[axis]
        return float(self.domain_center[axis_id])
    
    def __repr__(self) -> str:
        return f"QuokkaDataset(path='{self.path}')"
    
    def __str__(self) -> str:
        return (
            f"QuokkaDataset: {os.path.basename(self.path)}\n"
            f"  Domain: {self.domain_dimensions}\n"
            f"  Time: {self.current_time}\n"
            f"  Fields: {len(self.fields)} available"
        )
