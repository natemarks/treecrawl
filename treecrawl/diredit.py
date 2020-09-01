import logging
import os
from .utility import find_path_to_ancestor, string_to_log_level, validate_path
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
        """Discover all the files in the root_dir

        :rtype: List[str]

        """
        from treecrawl.utility import get_all_files

        return get_all_files(self.root_dir)

    def filter_target_files(self):
        """List of files (absolute path strings) that should be processed

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
                msg = "DRY RUN: Would transform {s} to {d}".format(s=k, d=v)
            else:
                msg = "EXECUTE: Editing {s} to {d}".format(s=k, d=v)
            self.logger.info(msg)
            if not self.dry_run:
                self.transform_files(k, v)


class Transformer(object):
    """Transform a file or directory

    input and output should both be paths to files OR both be directories
    with the same structure

    """

    def __init__(
        self, input=None, output=None, log_level="INFO", dry_run=True
    ):
        import json

        if input is None:
            self._input = os.getcwd()
        else:
            self._input = validate_path(input)
        if output is None:
            self._output = self._input
        else:
            self.output = output
        self.logger = logging.getLogger(
            module_name + "." + self.__class__.__name__
        )
        self.log_level = string_to_log_level(log_level)
        self.logger.setLevel(self.log_level)
        self.dry_run = dry_run

        msg_dict = {
            "input": self.input,
            "output": self.output,
            "log_level": self.log_level,
            "dry_run": str(self.dry_run),
        }
        self.logger.info(json.dumps(msg_dict))
        self.run()

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self._input = validate_path(value)
        return self._input

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value
        return self._output

    def in_place(self):
        """Return true if teh output will overwrite the input

        :rtype: bool
        """
        return self._input == self._output

    def source_dest_as_dict(self):
        """If the target us a directory, return dict of input:output files

        The logic for selecting targets can be customized by overriding this
        method.

        :rtype: Dict[str, str]
        """
        from treecrawl.utility import (
            get_all_files,
            output_file_from_input_file,
        )

        res = {}
        if os.path.isfile(self.input):
            return {self.input: self.output}

        input_files = get_all_files(self.input)
        for file in input_files:
            if Transformer.is_target(file):
                # transform input file and write to destination
                # in the same relative path in the output dir
                res[file] = output_file_from_input_file(
                    self.input, self.output, file
                )

        return res

    @staticmethod
    def is_target(i_file):
        """Return True is the file meets criteria to be transformed

        This is used by filter_files to build a target list.  The base
        implementation edits all files. Override this method to customizing
        file targeting

        By default skip files ending in .skip

        :param str i_file: abs path to target candidate

        :rtype: bool
        """
        if str(i_file).endswith(".skip"):
            return False
        return os.path.isfile(i_file)

    def transform(self, source_file, destination_file):
        """Override this with transformation logic

        read the soure_file, do whatever and write to destination_file

        :param str source_file: read this file as input
        :param str destination_file: write transformed file here

        """
        raise NotImplementedError

    def run(self):
        for k, v in self.source_dest_as_dict().items():
            if v is None:
                v = k
            if self.dry_run:
                msg = "DRY RUN: Would transform {s} to {d}".format(s=k, d=v)
            else:
                msg = "EXECUTE: Editing {s} to {d}".format(s=k, d=v)
            self.logger.info(msg)
            if not self.dry_run:
                self.transform(k, v)

    @staticmethod
    def write_string_to_output(s, o):
        """writes a string to a an absolute file path

        also creates necessary directories along the way

        :param str output_string: log string to process

        :rtype: List[Dict[str, str]]
        """
        from treecrawl.utility import string_to_file, mkdir_p

        if type(s) != str:
            msg = "Expected string input. Got {}".format(str(type(s)))
            raise RuntimeError(msg)
        # ensure directory pah exists
        mkdir_p(o, is_file=True)
        string_to_file(s, o)
