#!/usr/bin/env python3
"""
Standalone example demonstrating the usage of ArrayWrapper and ArrayView classes.

This script shows:
1. How to compile the wrapper classes
2. How to use them in practice
3. Ownership patterns and lifetime management
"""

import sys
import os
import tempfile
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

def build_wrappers():
    """Build the ArrayWrappers module."""
    import numpy as np
    from Cython.Build import cythonize
    from setuptools import setup, Extension
    
    # Paths
    data_dir = Path(__file__).parent.parent.parent / "autowrap" / "data_files" / "autowrap"
    
    # Create extension
    ext = Extension(
        "ArrayWrappers",
        sources=[str(data_dir / "ArrayWrappers.pyx")],
        include_dirs=[str(data_dir), np.get_include()],
        language="c++",
        extra_compile_args=["-std=c++11"],
    )
    
    # Build in temporary directory
    build_dir = tempfile.mkdtemp()
    
    setup(
        name="ArrayWrappers",
        ext_modules=cythonize([ext], language_level=3),
        script_args=['build_ext', '--inplace', f'--build-lib={build_dir}'],
    )
    
    # Add build directory to path
    sys.path.insert(0, build_dir)
    return build_dir


def demo_owning_wrapper():
    """Demonstrate owning wrapper usage."""
    print("\n=== Demo 1: Owning Wrapper ===")
    print("Using ArrayWrapperDouble to own data")
    
    try:
        from ArrayWrappers import ArrayWrapperDouble
        import numpy as np
        
        # Create wrapper with size
        wrapper = ArrayWrapperDouble(size=5)
        print(f"Created wrapper with size: {wrapper.size()}")
        
        # Get numpy array view
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
        print(f"NumPy array: {arr}")
        
        # Modify through numpy
        arr[:] = [1.0, 2.0, 3.0, 4.0, 5.0]
        print(f"After modification: {arr}")
        
        # Verify persistence
        arr2 = np.asarray(wrapper)
        arr2.base = wrapper
        print(f"Verified persistence: {arr2}")
        
        # Perform numpy operations
        print(f"Sum: {np.sum(arr2)}")
        print(f"Mean: {np.mean(arr2)}")
        
    except ImportError as e:
        print(f"Could not import ArrayWrappers: {e}")
        print("You may need to compile it first using: python setup.py build_ext --inplace")


def demo_view_wrapper():
    """Demonstrate view wrapper usage."""
    print("\n=== Demo 2: View Wrapper (Simulated) ===")
    print("In practice, views would wrap C++ reference returns")
    
    try:
        from ArrayWrappers import ArrayWrapperDouble, ArrayViewDouble
        import numpy as np
        
        # Create owner
        owner = ArrayWrapperDouble(size=3)
        owner_arr = np.asarray(owner)
        owner_arr.base = owner
        owner_arr[:] = [10.0, 20.0, 30.0]
        print(f"Owner data: {owner_arr}")
        
        # In real usage, you'd get pointer from C++ reference:
        # view = ArrayViewDouble(cpp_ref.data(), cpp_ref.size(), owner=cpp_obj)
        print("\nNote: ArrayView would typically be created from C++ reference returns")
        print("      where it provides zero-copy access to internal C++ data")
        
    except ImportError as e:
        print(f"Could not import ArrayWrappers: {e}")


def demo_const_view():
    """Demonstrate const view usage."""
    print("\n=== Demo 3: Const View ===")
    print("Using ConstArrayView for read-only access")
    
    try:
        from ArrayWrappers import ConstArrayViewDouble, ArrayWrapperDouble
        import numpy as np
        
        # In practice, this would wrap a const reference return from C++
        print("ConstArrayView enforces read-only access via buffer protocol")
        print("Attempts to get writable buffer will raise BufferError")
        
    except ImportError as e:
        print(f"Could not import ArrayWrappers: {e}")


def demo_type_variants():
    """Demonstrate different type variants."""
    print("\n=== Demo 4: Type Variants ===")
    
    try:
        from ArrayWrappers import ArrayWrapperFloat, ArrayWrapperDouble, ArrayWrapperInt
        import numpy as np
        
        # Float wrapper
        float_wrapper = ArrayWrapperFloat(size=3)
        float_arr = np.asarray(float_wrapper)
        float_arr.base = float_wrapper
        float_arr[:] = [1.5, 2.5, 3.5]
        print(f"Float array (dtype={float_arr.dtype}): {float_arr}")
        
        # Double wrapper
        double_wrapper = ArrayWrapperDouble(size=3)
        double_arr = np.asarray(double_wrapper)
        double_arr.base = double_wrapper
        double_arr[:] = [1.0, 2.0, 3.0]
        print(f"Double array (dtype={double_arr.dtype}): {double_arr}")
        
        # Int wrapper
        int_wrapper = ArrayWrapperInt(size=3)
        int_arr = np.asarray(int_wrapper)
        int_arr.base = int_wrapper
        int_arr[:] = [10, 20, 30]
        print(f"Int array (dtype={int_arr.dtype}): {int_arr}")
        
    except ImportError as e:
        print(f"Could not import ArrayWrappers: {e}")


def main():
    """Run all demos."""
    print("ArrayWrapper Demonstration")
    print("=" * 60)
    
    # Check if module is already built
    try:
        import ArrayWrappers
        print("ArrayWrappers module found!")
    except ImportError:
        print("ArrayWrappers module not found.")
        print("To build it, run from the repository root:")
        print("  cd autowrap/data_files/autowrap")
        print("  python -m pip install numpy cython")
        print("  cythonize -i ArrayWrappers.pyx")
        print()
    
    # Run demos
    demo_owning_wrapper()
    demo_view_wrapper()
    demo_const_view()
    demo_type_variants()
    
    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("\nKey takeaways:")
    print("1. Owning wrappers manage their own memory")
    print("2. Views provide zero-copy access to C++ data")
    print("3. Const views enforce read-only access")
    print("4. Always set numpy_array.base to keep wrapper alive")
    print("5. Multiple type variants available (float, double, int)")


if __name__ == "__main__":
    main()
