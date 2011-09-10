"""
This file is a part of
poproofread -- A po-file and podiff proofreader
Copyright (C) 2011 Kenneth Nielsen <k.nielsen81@gmail.com>

This program is free software: you can redistribute it and/or modify
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

import os, json
from custom_exceptions import FileError

class FileIO():
    """ This class provides the file IO functionality """

    def __init__(self):
        """ Initiate variables and file states """
        self.ppr_file = None
        self.out_file = None


    def read(self, input_file):
        """ Read content dependent on filetype """
        if os.path.splitext(input_file)[1] == '.out':
            if os.path.splitext(os.path.splitext(input_file)[0])[1] == 'ppr':
                """ We have tried to open the out file, overwrite and try to
                open the .ppr file """
                content = self.__read_ppr(os.path.splitext(input_file)[0])
        elif os.path.splitext(input_file)[1] == '.ppr':
            content = self.__read_ppr(input_file)
        else:
            content = self.__read_new(input_file)
        return content

    def __read_ppr(self, input_file):
        """ Read content from .ppr file """
        self.ppr_file = input_file
        self.out_file = input_file + '.out'
        self.__check_ppr_and_out_file(self.ppr_file, self.out_file, True)

        with open(self.input_file) as f:
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
        
        with open(input_file) as f:
            diff_chunks = f.read().split('\n\n')

        diff_list = [{'diff_chunk':diff, 'comment':'', 'inline':False}
                     for diff in diff_chunks]

        return {'text':diff_list, 'encoding':'utf-8', 'bookmark':None}

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
        self.__write_to_ppr(self, content)
        self.__write_to_out(self, content)

    def __write_to_ppr(self, content):
        pass
    
    def __write_to_out(self, content):
        pass

