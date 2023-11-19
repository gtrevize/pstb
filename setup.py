from setuptools import find_packages, setup

# Define package metadata
NAME = "pstb"
VERSION = "0.0.1"
DESCRIPTION = "Easy Toolbox for Python"
AUTHOR = "Golan Trevize"
EMAIL = "gtrevize66@protonmail.com"
URL = "https://github.com/gtrevize/pstb.git"

# Specify package requirements
INSTALL_REQUIRES = [
    "requests>=2.0.0",
    "numpy>=1.0.0",
]

# Locate and include all packages in the 'src' directory
PACKAGES = find_packages(where="src")
PACKAGE_DIR = {"": "src"}

# Define additional package data, such as data files or package-specific configuration
PACKAGE_DATA = {
    "pstb": ["data/*.json"],
}

# Define entry points, if applicable (e.g., console scripts)
ENTRY_POINTS = {
    "console_scripts": [
        "pstb-cli = pstb.cli:main",
    ],
}

# Create the setup configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=PACKAGES,
    package_dir=PACKAGE_DIR,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    python_requires=">=3.6",
)
