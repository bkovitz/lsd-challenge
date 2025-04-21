project = "LSD"
copyright = "2025, Adam"
author = "Adam"
release = "WIP"

html_theme = "furo"

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/scroll-start.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

templates_path = ["_templates"]

extensions = [
    "sphinx.ext.autodoc",  # Core autodoc
    "sphinx.ext.napoleon",  # Google/Numpy docstring support
    "sphinx.ext.viewcode",  # Add source links
    "sphinx.ext.autosummary",  # Generate summary tables
    "sphinx_git",
]

# Enable autodoc to scan your project
import os
import sys

sys.path.insert(0, os.path.abspath("../"))  # Path to your code
