#!/usr/bin/env python
"""Script to create Sphinx documentation demo for autowrap inheritance fixes"""
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result

def main():
    # Get the project root
    project_root = Path(__file__).parent.absolute()
    demo_dir = project_root / "docs_test" / "sphinx_demo"
    
    # Clean up if exists
    if demo_dir.exists():
        print(f"Cleaning up existing demo directory: {demo_dir}")
        shutil.rmtree(demo_dir)
    
    demo_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(demo_dir)
    
    print("=" * 70)
    print("Step 1: Generating autowrapped module")
    print("=" * 70)
    
    # Generate the autowrapped code
    # Using demo_inheritance which has multiple inherited methods to better demonstrate grouping
    pxd_files = [
        str(project_root / "tests" / "test_files" / "demo_inheritance" / "A.pxd"),
        str(project_root / "tests" / "test_files" / "demo_inheritance" / "B.pxd"),
    ]
    
    run_command([
        "autowrap",
        "--out", "moduleB.pyx"
    ] + pxd_files)
    
    print("\n" + "=" * 70)
    print("Step 2: Creating setup.py to build the module")
    print("=" * 70)
    
    # Create setup.py
    include_path = str(project_root / "tests" / "test_files" / "demo_inheritance")
    setup_py_content = f'''from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import pkg_resources

data_dir = pkg_resources.resource_filename("autowrap", "data_files")
include_dir = os.path.join(data_dir, "autowrap")

ext = Extension(
    "moduleB",
    sources=["moduleB.pyx"],
    language="c++",
    include_dirs=[include_dir, data_dir, "{include_path}"],
)

setup(
    ext_modules=cythonize([ext], language_level="3"),
    zip_safe=False,
)
'''
    
    with open("setup.py", "w") as f:
        f.write(setup_py_content)
    
    print("\n" + "=" * 70)
    print("Step 3: Building the Cython extension module")
    print("=" * 70)
    
    run_command(["python", "setup.py", "build_ext", "--inplace"])
    
    print("\n" + "=" * 70)
    print("Step 4: Setting up Sphinx")
    print("=" * 70)
    
    
    sphinx_config = [
        "y", 
        ".", 
        "_build",  
        "y",  
        "n",  
    ]
    

    quickstart_input = "\n".join(sphinx_config) + "\n"
    run_command(
        ["sphinx-quickstart", "-q", "--sep", "-p", "Autowrap Demo", 
         "-a", "Test", "-v", "1.0", "--ext-autodoc", "--ext-viewcode", "."],
        check=False  
    )
    
    print("\n" + "=" * 70)
    print("Step 5: Configuring Sphinx conf.py")
    print("=" * 70)
    
    # Read and modify conf.py
    conf_py_path = Path("conf.py")
    if conf_py_path.exists():
        with open(conf_py_path, "r") as f:
            conf_content = f.read()
        
        # Add path configuration if not already present
        if "sys.path.insert" not in conf_content:
            # Find the extensions line and add after it
            lines = conf_content.split("\n")
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                # Add after extensions or after imports
                if "extensions = [" in line or (i > 0 and "import sys" in lines[i-1] and "import os" in line):
                    if "sys.path.insert" not in conf_content:
                        new_lines.append("")
                        new_lines.append("# Add current directory to path for autodoc")
                        new_lines.append("import sys")
                        new_lines.append("import os")
                        new_lines.append("sys.path.insert(0, os.path.abspath('.'))")
                        new_lines.append("")
                        new_lines.append("# Order members by source to preserve class-defined vs inherited grouping")
                        new_lines.append("autodoc_member_order = 'bysource'")
                        break
        
        with open(conf_py_path, "w") as f:
            f.write("\n".join(new_lines) if isinstance(new_lines, list) else conf_content)
    else:
        
        conf_content = '''# Configuration file for the Sphinx documentation builder.
import sys
import os

project = 'Autowrap Demo'
copyright = '2024, Test'
author = 'Test'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'default'

# Add current directory to path for autodoc
sys.path.insert(0, os.path.abspath('.'))

# Order members by source to preserve class-defined vs inherited grouping
autodoc_member_order = 'bysource'
'''
        with open(conf_py_path, "w") as f:
            f.write(conf_content)
    
    print("\n" + "=" * 70)
    print("Step 6: Creating documentation content")
    print("=" * 70)
    
    # Create index.rst
    index_rst_content = '''Autowrap Inheritance Documentation Demo
========================================

This page demonstrates the Sphinx RST syntax for inheritance links and inherited method notation.

The ``Bklass`` class inherits from ``A_second``, and this should be shown with a clickable link.

Module Documentation
--------------------

.. automodule:: moduleB
   :members:
   :undoc-members:
   :show-inheritance:

Bklass Class
------------

.. autoclass:: moduleB.Bklass
   :members:
   :show-inheritance:
   :inherited-members:

   This class demonstrates:
   
   - Inheritance documentation with Sphinx RST syntax (``:py:class:`A_second``)
   - Inherited methods grouped separately from class-defined methods
   - "Inherited from" notation in method docstrings

A_second Base Class
-------------------

.. autoclass:: moduleB.A_second
   :members:
   :show-inheritance:

This is the base class that ``Bklass`` inherits from.
'''
    
    with open("index.rst", "w") as f:
        f.write(index_rst_content)
    
    print("\n" + "=" * 70)
    print("Step 7: Building HTML documentation")
    print("=" * 70)
    
    # Build the documentation
    run_command(["sphinx-build", "-b", "html", ".", "_build/html"])
    
    html_path = Path("_build/html/index.html").absolute()
    
    print("\n" + "=" * 70)
    print("SUCCESS! Documentation generated")
    print("=" * 70)
    print(f"\nHTML documentation is available at:")
    print(f"  {html_path}")
    print(f"\nTo view it, run:")
    print(f"  open {html_path}  # macOS")
    print(f"  xdg-open {html_path}  # Linux")
    print(f"  start {html_path}  # Windows")
    
    # Try to open automatically
    try:
        import webbrowser
        webbrowser.open(f"file://{html_path}")
        print("\nOpened in default browser!")
    except Exception as e:
        print(f"\nCould not open browser automatically: {e}")
        print("Please open the file manually.")
    
    print("\n" + "=" * 70)
    print("What to verify:")
    print("=" * 70)
    print("1. The Bklass class docstring should show:")
    print("   '-- Inherits from :py:class:`A_second`' with a clickable link")
    print("2. The callA2() method should show:")
    print("   'Inherited from :py:class:`A_second`.' with a clickable link")
    print("3. Methods should be grouped: class-defined methods first, inherited after")
    print("=" * 70)

if __name__ == "__main__":
    main()

