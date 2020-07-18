"""Helpers for using test data

"""
from .utility import file_to_string, find_path_to_subdirectory
from typing import List, Tuple


class TestData(object):
    """ Test helper object representing the test and test case data

    TestData gives pytests access to test data.  It's instantiated
    for each test case iteration. It assumes that every test name is unique and
    has a corresponding directory name in the project. It furter assumes that
    each test is parameterized with a list of test cases.  Each of these test
    cases has a corresponding directory immediately below the test directory.
    See the usage document for examples.


    """

    def __init__(self, test_name, temp_dir):
        self.temp_dir = temp_dir
        self.test_name = test_name
        self.test_directory_path = self._get_test_directory()

    def _get_test_directory(self):
        tdp = find_path_to_subdirectory(self.test_name)
        if len(tdp) == 0:
            raise RuntimeError(
                "Found no matching test directory: {}".format(self.test_name)
            )
        if len(tdp) > 1:
            msg = "Found more than one test directory. \
            This will be confusing. Please resolve it.: \n{}".format(
                str(tdp)
            )
            raise RuntimeError(msg)
        return tdp[0]

    def project_test_data_path(self):
        """Return the absolute path to the project test data

        Returns:
            str: a valid absolute path to the directory containing all the test
            case data for the test
        """
        from pathlib import Path

        # first find a directory in the project that's known to contain the
        # test data
        pp = ""

        # find the right project test data for the current test
        for path in Path(pp).rglob(self.test_name):
            # this will return on the first match
            return str(path)

    def copy_test_data_to_temp(self, test_case):
        """Copy the test data directory into the temporary test dir

        Args:
            temp_test_dir (str): copy the project test data to this temp test
            data location
        """
        import os
        import shutil

        source = os.path.join(self.test_directory_path, test_case)
        self.temp_case_data = os.path.join(
            str(self.temp_dir), *[self.test_name, test_case]
        )
        self.intial = os.path.join(self.temp_case_data, "initial")
        self.expected = os.path.join(self.temp_case_data, "expected")
        shutil.copytree(source, self.temp_case_data)

    def files_to_compare(self) -> List[Tuple[str, str]]:
        """Return list of pairs of objects that assert can compare

        Returns:
            List[Tuple[str, str]]: list of string pairs that can be compared by
            assert
        """
        import os

        result = []

        for file in os.listdir(self.intial):
            t_file_path = os.path.join(self.intial, file)
            e_file_path = os.path.join(self.expected, file)
            t_file_contents = file_to_string(t_file_path)
            if os.path.exists(e_file_path):
                e_file_contents = file_to_string(e_file_path)
            else:
                e_file_contents = None
            result.append((t_file_contents, e_file_contents))
        pass
        return result
