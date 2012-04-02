# -*- coding: utf-8 -*-

"""
custom_exceptions.py
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


class FileError(Exception):
    """ Common exception for file errors """
    def __init__(self, filename, msg):
        # Make this more proper
        #Exception.__init__(self, msg)
        self.filename = filename
        self.msg = msg
        self.title = 'File Error'


class FileWarning():
    """ Common warning for file operations """
    def __init__(self, filename, msg):
        self.filename = filename
        self.msg = msg
        self.title = 'File Warning'


class UnhandledException(Exception):
    """ This is thrown if we end up in a really bad place """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = ('Unhandled PoProofRead exception. This should not happen!'
                    '\n\nPlease report it as a bug at '
                    'https://bugs.launchpad.net/poproofread and include this '
                    'error message: {0}').format(msg)
