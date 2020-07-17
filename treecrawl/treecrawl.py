import logging
import sys
from typing import Dict, List

module_name = str(__name__)
module_logger = logging.getLogger(module_name)
module_logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    '%(asctime)s - {%(name)s} - {%(filename)s:%(funcName)s:%(lineno)d} - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)

module_logger.addHandler(ch)


def string_to_log_level(log_level_string):
    """ Given a string convert it to a logging level for use by logging.log

    Accept the string ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG') or the
    integer ('10', '20', '30', '40', '50') format

    :param str log_level_string: case insensitive

    """
    import logging
    if log_level_string.upper() in [
            'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'
    ]:
        return getattr(logging, log_level_string.upper())

    integer_levels = {
        '50': 'CRITICAL',
        '40': 'ERROR',
        '30': 'WARNING',
        '20': 'INFO',
        '10': 'DEBUG',
    }
    return getattr(logging, integer_levels[log_level_string])


def find_path_to_ancestor(target_dir='clean_unicode'):
    """ Find path to parent directory among the ancestors

    target_dir is the base name of a directory  (without path separator) that
    will be discovered from amogn the parent directories

    If the target_dir is given a strinf that contains a path separator, it just
    returns the target_dir.  This is useful for testing, so we can explicitly
    pass an absolute path.

    :param str target_dir: target directory

    :rtype: str
    """
    import os
    if os.path.sep in target_dir:
        return target_dir
    ancestors = os.getcwd().split(os.path.sep)
    if target_dir not in ancestors:
        raise RuntimeError(
            'Current directory is not a subdirectory of {}'.format(target_dir))
    else:
        # iterate through the last dirs until we hit the one we want
        while not ancestors[-1] == target_dir:
            ancestors.pop()
    # rejoin: we lose the first separator in the split/join
    return os.path.sep + os.path.join(*ancestors)


def file_to_string(file_path):
    """ Return file contents as a string

    :param str file_path: absolute path to a file
    :rtype: str

    """
    with open(file_path, "r") as f:
        try:
            data = f.read()
        except UnicodeDecodeError:
            data = ""
    return data


def string_to_file(input_string, file_path):
    """ Write/Over-write a file's contents with a string


    :param str input_string: string data
    :param str file_path: absolute path to a file
    """
    with open(file_path, "w") as f:
        f.write(input_string)


class DirEdit(object):
    def __init__(self, log_level='INFO', root_dir=None, dry_run=True):
        # root_dir example: 'dna' -> '/full/path/to/dna'
        self.root_dir = find_path_to_ancestor(root_dir)  # type: str
        self.logger = logging.getLogger(module_name + '.' +
                                        self.__class__.__name__)
        self.log_level = string_to_log_level(log_level)
        self.logger.setLevel(self.log_level)
        self.dry_run = dry_run
        self.run()

    def get_all_files(self):
        """ Discover all the files in the root_dir

        :rtype: List[str]

        """
        import os
        res = []
        # ?borrowed? from https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
        for (dirpath, dirnames, filenames) in os.walk(self.root_dir):
            res += [os.path.join(dirpath, file) for file in filenames]
        return res

    def filter_target_files(self):
        """ List of files (absolute path strings) that should be processed

        Override this method to customize. The base implementation returns
        everything
        """
        res = []
        for this_file in self.get_all_files():
            res.append(this_file)
        return res

    def src_dest_file_pairs(self):
        """Get dict of target file: output file

        {'/a/b/c/file.txt': '/a/b/c/new_file.txt'} would mean we're editing
        file.txt but writing the results to new_file.txt in the same directory.
        if the key and value are the same OR if the value is None, edit the file
        in place.

        override this file with an algorithm to write to some other predictable
        location. The default is to make the key and value the same

        Returns: Dict[str, str]: [description]
        """
        result = {}
        for this_file in self.filter_target_files():
            result[this_file] = this_file
        return result

    def transform_files(self, source_file, destination_file):
        raise NotImplementedError

    def run(self):
        for k, v in self.src_dest_file_pairs().items():
            if v == None:
                v = k
            if self.dry_run:
                msg = "DRY RUN: Would tranmsform {s} to {d}".format(s=k, d=v)
            else:
                msg = "EXECUTE: Editing {s} to {d}".format(s=k, d=v)
            self.logger.info(msg)
            if not self.dry_run:
                self.transform_files(k, v)


class TestData(object):
    """ Test helper object representing the test and test case data

    This object is instantiated once per test. It copies the project test data (PTD) into temp directories created
    for each test by pytest.tmp_path. the copied data, temporary test data, (TTD) are used by the tests as input and
    expected content.

    Each pytest contains multiple cases. Each case has it's own data set with predictably located artifacts. The
    relative paths to these artifacts are stored i in TestData class attributes (DNA_DIR, etc)

    test_manifest.TestData.copy_test_data_to_temp  copies the case directories from the project to the temporary dirs
    for testing

    """
    def __init__(self, test_name):
        self.test_name = test_name
        self.project_test_data = self.project_test_data_path()
        # temp_test_data is the directory in tmp_path that contains all the cases for this test
        self.temp_test_data = None

    def artifact_path_for_case(self, case, artifact_path):
        """ Return the absolute path to the temporary test data for the current  test and test case.

        join the tmp directory with the test case name and the constant relative path to the artifact

        :param str case: the current test case
        :param str artifact_path: the path to the artifact relative to the temp + case directory

        NOTE: TestData users should just use the class attribute they want as the artifact_path parameter
        example:
        expected_manifest_markdown_file = test_data.artifact_path_for_case(test_case, TestData.EXPECTED_MANIFEST_MD)

        :rtype: str
        """
        import os

        return os.path.join(self.temp_test_data, case, artifact_path)

    def project_test_data_path(self):
        """ Return the absolute path to the project test data

        The project test data is copied into temporary directories each time the tests are run. Inside each test data 
        are directories with names matching the test cases for the test


        :rtype: str # a valid absolute path to the directory containing all the test case data for the test
        """
        from pathlib import Path
        # first find a directory in the project that's known to contain the test data
        pp = find_path_to_ancestor()
        # find the right project test data for the current test
        for path in Path(pp).rglob(self.test_name):
            # this will return on the first match
            return str(path)

    def copy_test_data_to_temp(self, temp_test_dir):
        """ Copy the test data directory into the temporary test dir
        
        if this succeeds, set the temp test data directory
        
        :param str temp_test_dir: copy the project test data to this temp test data location
        
        :rtype: List[Dict[str, str]]
        """
        import os
        from pathlib import Path
        import shutil
        # tp is source data in the project tree
        tdp = self.project_test_data_path()

        for path in Path(tdp).glob('*'):
            dest = os.path.join(temp_test_dir, path.name)
            # opy copy directories
            if not os.path.isdir(str(path)):
                continue
            shutil.copytree(str(path), dest)
        self.temp_test_data = temp_test_dir

    def files_to_compare(self, test_case):
        """Return list of pairs of objects that assert can compare

        Find the initial and expected dirs in teh test case dir
        Iterate the files in initial, find match for each in expected
        convert the files to assert-comparable objects, make a tuple and append to the result list. 
        if the matching fiule isn't found, use None


        Args:
            test_case (str): The test case used to find the initial/ expected dirs to look in for files to compare

        Returns:
            [type]: [description]
        """
        import os
        result = []

        initial_dir = os.path.join(self.temp_test_data,
                                   *[test_case, "initial"])
        for file in os.listdir(initial_dir):
            t_file_path = os.path.join(initial_dir, file)
            e_file_path = os.path.join(
                initial_dir.replace('initial', 'expected'), file)
            t_file_contents = file_to_string(t_file_path)
            if os.path.exists(e_file_path):
                e_file_contents = file_to_string(e_file_path)
            else:
                e_file_contents = None
            result.append((t_file_contents, e_file_contents))
        pass
        return result
