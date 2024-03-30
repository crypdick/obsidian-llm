"""Sphinx configuration."""

project = "Obsidian Llm"
author = "Richard Decal"
copyright = "2024, Richard Decal"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
