from setuptools import setup, find_packages

# Read the contents of README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cyberpi",  # Project name (used on PyPI)
    version="0.1.0",   # Version number (follows semantic versioning)
    author="Your Name",
    author_email="cody@mccomber.me",
    description="A short description of cyberpi",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Specifies README format
    url="https://github.com/CodyMcC/cyberpi",  # Project homepage
    packages=find_packages(where=".", exclude=["tests", "docs"]),  # Automatically find packages
    install_requires=[
        # "requests>=2.25.1",  # Runtime dependencies
        # "numpy>=1.21.0",
        "tesla-fleet-api>=0.1.1"
    ],
    python_requires=">=3.9",  # Minimum Python version
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    entry_points={
        "console_scripts": [
            "cyberpi=cyberpi.cli:main",  # Example CLI script (if applicable)
        ],
    },
)
