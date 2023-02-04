# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Tally SDK'
copyright = '2023, Geir Freysson'
author = 'Geir Freysson'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.napoleon', 'sphinx.ext.autosectionlabel', 'sphinx_design', 'myst_nb']
myst_enable_extensions = ["colon_fence"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

napoleon_numpy_docstring = True

jupyter_execute_notebooks = "off"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_theme_options = {
    "repository_url": "https://github.com/datasmoothie/tally-client",
    "use_repository_button": True,
    "use_download_button": False,
    "use_fullscreen_button": False
  }
html_title = ""
html_logo = "datasmoothie-logo-h25_padding_2x.png"
html_static_path = ['_static']
