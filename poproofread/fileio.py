# -*- coding: utf-8 -*-

"""
fileio.py
This file is a part of PoProofRead

Copyright (C) 2011 Kenneth Nielsen <k.nielsen81@gmail.com>

PoProofRead is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
import codecs
import re
from custom_exceptions import FileError, FileWarning


class FileIO():
    """ This class provides the file IO functionality """

    def __init__(self):
        """ Initiate variables """
        self.ppr_file = None
        self.out_file = None

    def read(self, input_file):
        """ Read content dependent on filetype """
        warnings = []
        if os.path.splitext(input_file)[1] == '.out':
            if os.path.splitext(os.path.splitext(input_file)[0])[1] == '.ppr':
                # We have tried to open the out file, overwrite and try to open
                # the .ppr file
                content = self.__read_ppr(os.path.splitext(input_file)[0])
                actual_file = os.path.splitext(input_file)[0]
                warning_text = ('Loaded .ppr instead of .ppr.out since that '
                                'is the one we need to load to continue '
                                'previous work')
                warnings.append(FileWarning(input_file, warning_text))
        elif os.path.splitext(input_file)[1] == '.ppr':
            content = self.__read_ppr(input_file)
            actual_file = input_file
            print 'Loaded .ppr'
        else:
            if os.access(input_file + '.ppr', os.F_OK):
                actual_file = input_file + '.ppr'
                content = self.__read_ppr(actual_file)
                warning_text = ('Loaded .ppr instead of source to prevent '
                                'overwriting existing work in the .ppr file'
                                '\n\nIf you wish to reset your proofreading '
                                'you must delete the .ppr and .ppr.out files.')
                warnings.append(FileWarning(input_file, warning_text))
            else:
                content = self.__read_new(input_file)
                actual_file = input_file + '.ppr'
                print 'Loaded new diff'
        return (content, actual_file, warnings)

    def __read_ppr(self, input_file):
        """ Read content from .ppr file """
        self.ppr_file = input_file
        self.out_file = input_file + '.out'
        self.__check_ppr_and_out_file(self.ppr_file, self.out_file, True)

        with open(input_file) as f:
            return json.loads(f.read())

    def __read_new(self, input_file):
        """ Read content from new file """
        self.ppr_file = input_file + '.ppr'
        self.out_file = self.ppr_file + '.out'
        self.__check_ppr_and_out_file(self.ppr_file, self.out_file, False)

        if not os.access(input_file, os.F_OK):
            raise FileError(input_file, 'The file does not exist.')
        if not os.access(input_file, os.R_OK):
            raise FileError(input_file, 'The file is not readable.')

        # Detect charater encoding
        encoding = None
        # Search for diff type (+- ) line and charset in Content-Type line
        charset_pattern = r'^(.*)"Content-Type:.*charset=([a-zA-Z0-9-]*).*$'
        with open(input_file) as f:
            for line in f.readlines():
                if line == '\n':
                    break
                else:
                    search = re.search(charset_pattern, line)
                    try:
                        # A diff has a character before #Content-Type...
                        if len(search.group(1)) > 0:
                            if search.group(1) in ['+', ' ']:
                                encoding = search.group(2)
                        # a reular po-file does not
                        else:
                            encoding = search.group(2)
                    except AttributeError:
                        pass

        # Continue charater encoding code

        with open(input_file) as f:
            diff_chunks = f.read().split('\n\n')

        diff_list = [{'diff_chunk': diff, 'comment': '', 'inline': False}
                     for diff in diff_chunks]

        return {'text': diff_list, 'encoding': 'utf-8', 'bookmark': None,
                'current': 0, 'no_chunks': len(diff_list)}

    def __check_ppr_and_out_file(self, ppr_file, out_file, existing):
        """ Check file permissions """
        if existing:
            if not os.access(ppr_file, os.F_OK):
                raise FileError(ppr_file, 'The file does not exist.')
            if not os.access(ppr_file, os.R_OK):
                raise FileError(ppr_file, 'The file is not readable.')
            if not os.access(ppr_file, os.W_OK):
                raise FileError(ppr_file, 'The file is not writeable.')
        else:
            if os.access(ppr_file, os.F_OK):
                if not os.access(ppr_file, os.R_OK):
                    raise FileError(ppr_file, 'The file is not readable.')
                if not os.access(ppr_file, os.W_OK):
                    raise FileError(ppr_file, 'The file is not writeable.')
            else:
                dirname = os.path.dirname(ppr_file)\
                    if os.path.dirname(ppr_file) != '' else '.'
                if not (os.access(dirname, os.W_OK) and
                        os.access(dirname, os.X_OK)):
                    raise FileError(ppr_file, 'The file cannot be created.')

        if os.access(out_file, os.F_OK):
            if not os.access(self.out_file, os.W_OK):
                raise FileError(out_file, 'The file is not writeable.')
        else:
            dirname = os.path.dirname(out_file)\
                if os.path.dirname(out_file) != '' else '.'
            if not (os.access(dirname, os.W_OK) and
                    os.access(dirname, os.X_OK)):
                raise FileError(out_file, 'The file cannot be created.')

    def write(self, content):
        """ Write content to ppr and out file """
        self.__write_to_ppr(content)
        self.__write_to_out(content)

    def __write_to_ppr(self, content):
        """ Write json representation of content to .ppr file """
        with open(self.ppr_file, 'w') as f:
            f.write(json.dumps(content))

    def __write_to_out(self, content):
        """ Write out file """
        with codecs.open(self.out_file, encoding='utf-8', mode='w') as f:
            for comment in content['text']:
                if comment['comment'] != '':
                    if not comment['inline']:
                        f.write(comment['diff_chunk'] + '\n\n')
                    f.write(comment['comment'] + '\n\n')
