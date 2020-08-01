#!/usr/bin/env python

"""Tests for `treecrawl` package."""
import pytest
from treecrawl.utility import find_path_to_subdirectory, mkdir_p, get_all_files
from treecrawl.testdata import TestData


def test_find_path_to_subdirectory(tmp_path):
    import os

    target_dir = os.path.join(
        str(tmp_path), *["some", "path", "to", "testdata"]
    )
    mkdir_p(target_dir)
    ff = find_path_to_subdirectory("testdata", search_path=str(tmp_path))
    assert ff[0].endswith("testdata")


@pytest.mark.parametrize(
    "test_case", ["happy_path"],
)
def test_get_all_files(test_case, tmp_path, request):
    """Run and compare results to expected

    """

    # Instantiate a TestData object with the name of the test (originalname)
    t = TestData(request.node.originalname, str(tmp_path))
    # copy iitial and expected test case data to temp path
    t.copy_test_data_to_temp(test_case)
    # Execute against initial data
    res = get_all_files(tmp_path)
    assert len(res) == 3
