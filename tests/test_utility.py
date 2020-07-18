#!/usr/bin/env python

"""Tests for `treecrawl` package."""
from treecrawl.utility import find_path_to_subdirectory, mkdir_p


def test_find_path_to_subdirectory(tmp_path):
    import os

    target_dir = os.path.join(
        str(tmp_path), *["some", "path", "to", "testdata"]
    )
    mkdir_p(target_dir)
    ff = find_path_to_subdirectory("testdata", search_path=str(tmp_path))
    assert ff[0].endswith("testdata")
