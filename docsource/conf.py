# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# add root/docs for finding stubs and custom extension
sys.path.insert(0, Path(__file__).parent.resolve().as_posix())
# add root for finding module mcpq
sys.path.insert(0, Path(__file__).parents[1].resolve().as_posix())

import mcpq

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "MCPQ"
copyright = "2024, Felix Wallner"
author = "Felix Wallner"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc.typehints",
    "del_private_class_sig",
    "patch_inherited_bysource_order",
    "myst_parser",  # parsing markdown files
    # "sphinx.ext.viewcode",
    # "sphinx.ext.autosectionlabel",
]
autosummary_generate = True  # turn on autosummary

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "agogo"
html_static_path = ["_static"]


autodoc_default_options = {
    "member-order": "bysource",
    "members": True,
    "undoc-members": True,
    # "show-inheritance": False, # False shows Bases?
}
add_module_names = False
# nitpicky = True

# The full version, including alpha/beta/rc tags.
release = mcpq.__version__
# The short X.Y version.
version = release
