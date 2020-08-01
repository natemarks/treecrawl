import logging
from .utility import find_path_to_ancestor, string_to_log_level
from treecrawl.utility import create_module_logger

module_name = str(__name__)
module_logger = create_module_logger(module_name)


class DirEdit(object):
    def __init__(self, log_level="INFO", root_dir=None, dry_run=True):
        self.root_dir = find_path_to_ancestor(root_dir)  # type: str
        self.logger = logging.getLogger(
            module_name + "." + self.__class__.__name__
        )
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
        if the key and value are the same OR if the value is None, edit the
        file in place.

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
            if v is None:
                v = k
            if self.dry_run:
                msg = "DRY RUN: Would tranmsform {s} to {d}".format(s=k, d=v)
            else:
                msg = "EXECUTE: Editing {s} to {d}".format(s=k, d=v)
            self.logger.info(msg)
            if not self.dry_run:
                self.transform_files(k, v)
