"""
Keywords Translation Tool - Refactored Package

A comprehensive toolkit for multilingual keyword translation and entity linking
with support for multiple providers (OpenAI, Groq, Local LLM, DBPedia).
"""

# __version__ = "1.0.0"
# __author__ = "Keywords Translation Team"

from . import clients
from . import pipelines
from . import prompt
from . import utils

__all__ = [
    "clients",
    "pipelines",
    "prompt",
    "utils"
]

