# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Tally Python SDK'
copyright = '2023, Datasmoothie'
author = 'Datasmoothie'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  'sphinx.ext.autodoc', 
  'sphinx.ext.autosummary', 
  'sphinx.ext.napoleon', 
  'sphinx.ext.autosectionlabel', 
  'sphinx_design', 
  'myst_nb'
  ]

autosummary_generate = True  # Turn on sphinx.ext.autosummary
myst_enable_extensions = ["colon_fence"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

napoleon_numpy_docstring = True

nb_execution_mode = "auto"

import sys, os
#sys.path.insert(1, os.path.abspath('../'))
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../../'))
sys.path.append(os.path.abspath('../../../'))
sys.path.append(os.path.abspath('../tally/'))


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
html_logo = "_static/assets/images/datasmoothie-logo.svg"
html_static_path = ['_static']
html_css_files = ["assets/css/custom.css"]

