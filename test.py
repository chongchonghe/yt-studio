#!/usr/bin/env python3
"""
Test script for plot_quokka module.

This script validates the plot_quokka library by creating various
visualizations using the sample dataset data/plt00020.

Usage:
    python test.py
    
    # Or with a custom dataset path:
    python test.py /path/to/dataset

Output files are saved to the 'output/' directory.
"""

import os
import sys

# Add the module to path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def create_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def test_basic_slice(plotter, output_dir):
    """Test basic slice plot with default parameters."""
    print("\n" + "="*60)
    print("TEST 1: Basic slice plot (default parameters)")
    print("="*60)
    
    output_path = os.path.join(output_dir, "test1_basic_slice.png")
    result = plotter.slice("z", "density", output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Basic slice test passed")
    return True


def test_slice_with_colorbar(plotter, output_dir):
    """Test slice plot with colorbar enabled."""
    print("\n" + "="*60)
    print("TEST 2: Slice plot with colorbar")
    print("="*60)
    
    params = PlotParams(
        cmap="inferno",
        log_scale=True,
        colorbar=ColorbarParams(show=True, label="Density (g/cm³)"),
    )
    
    output_path = os.path.join(output_dir, "test2_slice_colorbar.png")
    result = plotter.slice("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Colorbar slice test passed")
    return True


def test_slice_with_scale_bar(plotter, output_dir):
    """Test slice plot with scale bar."""
    print("\n" + "="*60)
    print("TEST 3: Slice plot with scale bar")
    print("="*60)
    
    params = PlotParams(
        cmap="viridis",
        log_scale=True,
        scale_bar=ScaleBarParams(show=True),
        colorbar=ColorbarParams(show=True),
    )
    
    output_path = os.path.join(output_dir, "test3_slice_scalebar.png")
    result = plotter.slice("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Scale bar slice test passed")
    return True


def test_slice_different_axes(plotter, output_dir):
    """Test slice plots along different axes."""
    print("\n" + "="*60)
    print("TEST 4: Slice plots along different axes (x, y, z)")
    print("="*60)
    
    params = PlotParams(
        cmap="plasma",
        log_scale=True,
        colorbar=ColorbarParams(show=True),
    )
    
    for axis in ["x", "y", "z"]:
        output_path = os.path.join(output_dir, f"test4_slice_{axis}.png")
        result = plotter.slice(axis, "density", params=params, output=output_path)
        print(f"  Axis {axis}: {os.path.exists(result)}")
    
    print("  ✓ Multi-axis slice test passed")
    return True


def test_slice_with_annotations(plotter, output_dir):
    """Test slice plot with text annotations."""
    print("\n" + "="*60)
    print("TEST 5: Slice plot with annotations")
    print("="*60)
    
    params = PlotParams(
        cmap="viridis",
        log_scale=True,
        colorbar=ColorbarParams(show=True),
        annotations=AnnotationParams(
            show_timestamp=True,
            show_grids=True,
            top_left_text="Test Simulation",
            top_right_text="t = 0.0",
        ),
    )
    
    output_path = os.path.join(output_dir, "test5_slice_annotations.png")
    result = plotter.slice("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Annotated slice test passed")
    return True


def test_slice_with_particles(plotter, output_dir):
    """Test slice plot with particle overlay."""
    print("\n" + "="*60)
    print("TEST 6: Slice plot with particles")
    print("="*60)
    
    # Check if particles are available
    if plotter.dataset.particle_types:
        print(f"  Available particle types: {plotter.dataset.particle_types}")
        
        params = PlotParams(
            cmap="viridis",
            log_scale=True,
            colorbar=ColorbarParams(show=True),
            particles=ParticleParams(
                types=["CIC_particles"],
                size=5,
                color="red",
            ),
        )
        
        output_path = os.path.join(output_dir, "test6_slice_particles.png")
        result = plotter.slice("z", "density", params=params, output=output_path)
        
        print(f"  Output: {result}")
        print(f"  File exists: {os.path.exists(result)}")
    else:
        print("  No particles in dataset, skipping particle overlay")
    
    print("  ✓ Particle slice test passed")
    return True


def test_projection(plotter, output_dir):
    """Test projection plot."""
    print("\n" + "="*60)
    print("TEST 7: Projection plot")
    print("="*60)
    
    params = PlotParams(
        cmap="inferno",
        log_scale=True,
        colorbar=ColorbarParams(show=True),
    )
    
    output_path = os.path.join(output_dir, "test7_projection.png")
    result = plotter.project("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Projection test passed")
    return True


def test_weighted_projection(plotter, output_dir):
    """Test weighted projection plot."""
    print("\n" + "="*60)
    print("TEST 8: Weighted projection plot")
    print("="*60)
    
    params = PlotParams(
        cmap="magma",
        log_scale=True,
        colorbar=ColorbarParams(show=True),
    )
    
    output_path = os.path.join(output_dir, "test8_weighted_projection.png")
    result = plotter.project(
        "z", "density", 
        params=params, 
        weight_field="density",
        output=output_path
    )
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Weighted projection test passed")
    return True


def test_custom_width(plotter, output_dir):
    """Test slice plot with custom width (zoom)."""
    print("\n" + "="*60)
    print("TEST 9: Slice plot with custom width")
    print("="*60)
    
    params = PlotParams(
        cmap="viridis",
        log_scale=True,
        colorbar=ColorbarParams(show=True),
        width=WidthParams(value=0.5, unit="code_length"),
    )
    
    output_path = os.path.join(output_dir, "test9_custom_width.png")
    result = plotter.slice("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Custom width test passed")
    return True


def test_custom_color_limits(plotter, output_dir):
    """Test slice plot with custom color limits."""
    print("\n" + "="*60)
    print("TEST 10: Slice plot with custom color limits")
    print("="*60)
    
    # Get field extrema first
    field_info = plotter.get_field_info("density")
    print(f"  Field min: {field_info['min']:.2e}")
    print(f"  Field max: {field_info['max']:.2e}")
    
    # Use a subset of the range
    vmin = field_info['min'] * 10
    vmax = field_info['max'] / 10
    
    params = PlotParams(
        cmap="viridis",
        log_scale=True,
        vmin=vmin,
        vmax=vmax,
        colorbar=ColorbarParams(show=True),
    )
    
    output_path = os.path.join(output_dir, "test10_custom_limits.png")
    result = plotter.slice("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Custom color limits test passed")
    return True


def test_dataset_info(plotter):
    """Test dataset information retrieval."""
    print("\n" + "="*60)
    print("TEST 11: Dataset information")
    print("="*60)
    
    dataset = plotter.dataset
    
    print(f"  Path: {dataset.path}")
    print(f"  Domain dimensions: {dataset.domain_dimensions}")
    print(f"  Domain width: {dataset.domain_width}")
    print(f"  Current time: {dataset.current_time}")
    print(f"  Max level: {dataset.max_level}")
    print(f"  Number of fields: {len(dataset.fields)}")
    print(f"  Particle types: {dataset.particle_types}")
    
    print("\n  Available fields:")
    for i, field in enumerate(dataset.fields[:10]):
        print(f"    {field}")
    if len(dataset.fields) > 10:
        print(f"    ... and {len(dataset.fields) - 10} more")
    
    print("  ✓ Dataset info test passed")
    return True


def test_bytes_output(plotter):
    """Test getting image as bytes (for web frontend use)."""
    print("\n" + "="*60)
    print("TEST 12: Bytes output (for web frontend)")
    print("="*60)
    
    # Get bytes without saving to file
    image_bytes = plotter.slice("z", "density")
    
    print(f"  Output type: {type(image_bytes)}")
    print(f"  Output size: {len(image_bytes)} bytes")
    print(f"  Is PNG: {image_bytes[:8] == b'\\x89PNG\\r\\n\\x1a\\n'}")
    
    print("  ✓ Bytes output test passed")
    return True


def test_method_chaining(plotter, output_dir):
    """Test method chaining for parameter building."""
    print("\n" + "="*60)
    print("TEST 13: Method chaining for parameters")
    print("="*60)
    
    # Build params with method chaining
    params = (PlotParams(cmap="inferno", log_scale=True)
              .with_colorbar(show=True, label="Density")
              .with_scale_bar(show=True)
              .with_width(0.8, "code_length"))
    
    output_path = os.path.join(output_dir, "test13_method_chaining.png")
    result = plotter.slice("z", "density", params=params, output=output_path)
    
    print(f"  Output: {result}")
    print(f"  File exists: {os.path.exists(result)}")
    print("  ✓ Method chaining test passed")
    return True


def run_all_tests(dataset_path):
    """Run all tests."""
    print("="*60)
    print("PLOT_QUOKKA TEST SUITE")
    print("="*60)
    print(f"\nDataset: {dataset_path}")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir}")
    
    # Create plotter
    print("\nInitializing plotter...")
    try:
        plotter = QuokkaPlotter(dataset_path)
        print(f"Plotter initialized: {plotter}")
    except Exception as e:
        print(f"ERROR: Failed to initialize plotter: {e}")
        return False
    
    # Run tests
    tests = [
        (test_dataset_info, (plotter,)),
        (test_basic_slice, (plotter, output_dir)),
        (test_slice_with_colorbar, (plotter, output_dir)),
        (test_slice_with_scale_bar, (plotter, output_dir)),
        (test_slice_different_axes, (plotter, output_dir)),
        (test_slice_with_annotations, (plotter, output_dir)),
        (test_slice_with_particles, (plotter, output_dir)),
        (test_projection, (plotter, output_dir)),
        (test_weighted_projection, (plotter, output_dir)),
        (test_custom_width, (plotter, output_dir)),
        (test_custom_color_limits, (plotter, output_dir)),
        (test_bytes_output, (plotter,)),
        (test_method_chaining, (plotter, output_dir)),
    ]
    
    passed = 0
    failed = 0
    
    for test_func, args in tests:
        try:
            result = test_func(*args)
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n  ERROR in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {passed + failed}")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


def main():
    """Main entry point."""
    # Default dataset path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_dataset = os.path.join(script_dir, "..", "data", "plt00020")
    
    # Allow custom dataset path from command line
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = default_dataset
    
    # Resolve path
    dataset_path = os.path.abspath(dataset_path)
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset not found: {dataset_path}")
        print("\nUsage: python test.py [dataset_path]")
        print(f"Default path: {default_dataset}")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests(dataset_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
