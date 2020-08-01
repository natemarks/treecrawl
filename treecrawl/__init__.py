"""Top-level package for treecrawl."""

__author__ = """Nate Marks"""
__email__ = "npmarks@gmail.com"
__version__ = "0.1.7"


from .diredit import DirEdit
from .testdata import TestData
from .utility import (
    create_module_logger,
    file_to_string,
    find_path_to_ancestor,
    string_to_file,
    string_to_log_level,
    get_all_files,
    strip_prefix,
    strip_suffix,
)

__all__ = (
    "DirEdit",
    "TestData",
    "create_module_logger",
    "file_to_string",
    "find_path_to_ancestor",
    "string_to_file",
    "string_to_log_level",
    "get_all_files",
    "strip_prefix",
    "strip_suffix",
)
