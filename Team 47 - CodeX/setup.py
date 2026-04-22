# setup.py
import os
import sys
from setuptools import setup, Extension
import pybind11

# Determine compiler flags based on platform
if sys.platform == 'win32':
    extra_compile_args = ['/std:c++14', '/O2', '/EHsc']
else:
    extra_compile_args = ['-std=c++14', '-O3', '-Wall']

# Create the extension module
ext_modules = [
    Extension(
        'apt_engine',                          # Module name
        ['bindings.cpp'],                      # Source files
        include_dirs=[
            pybind11.get_include(),
            pybind11.get_include(user=True)
        ],
        language='c++',
        extra_compile_args=extra_compile_args,
        define_macros=[('VERSION_INFO', '"4.0"')],
    ),
]

setup(
    name='apt_engine',
    version='4.0',
    author='SecureBank',
    description='SecureBank APT Detection Engine',
    long_description='High-performance C++ APT detection with Python bindings',
    ext_modules=ext_modules,
    zip_safe=False,
    python_requires='>=3.8',
)