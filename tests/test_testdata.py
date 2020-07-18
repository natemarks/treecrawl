#!/usr/bin/env python

"""Tests for `treecrawl` package."""

import pytest
from treecrawl.diredit import DirEdit
from treecrawl.testdata import TestData


class Upperificator(DirEdit):
    """Convert file characters to upper case

    """

    def __init__(self, root_dir=None, dry_run=True):
        super().__init__(root_dir=root_dir, dry_run=dry_run)

    def transform_files(self, source_file, destination_file):
        from treecrawl.utility import file_to_string, string_to_file

        contents = file_to_string(source_file)
        contents = contents.upper()
        string_to_file(contents, destination_file)


@pytest.mark.parametrize(
    "test_case", ["pets", "cities"],
)
def test_upperificator(test_case, tmp_path, request):
    """Run and compare results to expected

    """
    # Instantiate a TestData object with the name of the test (originalname)
    t = TestData(request.node.originalname, str(tmp_path))
    # copy iitial and expected test case data to temp path
    t.copy_test_data_to_temp(test_case)
    # Execute against initial data
    Upperificator(root_dir=t.intial, dry_run=False)
    # compare all modified target files in initial against the matching
    # file in expected
    for cmp in t.files_to_compare():
        assert cmp[0] == cmp[1]
