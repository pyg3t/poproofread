# -*- coding: utf-8 -*-

"""
core.py
This file is a part of PoProofRead.

Copyright (C) 2011-2012 Kenneth Nielsen <k.nielsen81@gmail.com>

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

from fileio import FileIO


class PoProofRead():
    """ Main functionality for poproofread """

    def __init__(self):
        self.fileio = FileIO()
        self.active = False
        self.content = None

    def open(self, filename):
        self.content, actual_file, warning = self.fileio.read(filename)
        # The next line should only be executed if open was succesfull
        self.active = True
        return actual_file, warning

    def close(self):
        self.fileio.__init__()
        self.active = False
        self.content = None

    def save(self, clipboard=False):
        charset_warning, text = self.fileio.write(self.content, clipboard)
        if charset_warning is not None:
            self.content['encoding'] = 'utf-8'
        return charset_warning, text

    def move(self, amount=None, goto=None):
        if amount != None:
            self.content['current'] = self.content['current'] + amount
            # There has got to be a more pythonic way of doing this
            # index = max(0, min(index, len(List) - 1))
            if self.content['current'] < 0:
                self.content['current'] = 0
            if self.content['current'] >= self.content['no_chunks']:
                self.content['current'] = self.content['no_chunks'] - 1
        elif goto != None:
            if goto < 0:
                self.content['current'] = self.content['no_chunks'] - 1
            elif goto >= self.content['no_chunks']:
                self.content['current'] = self.content['no_chunks'] - 1
            else:
                self.content['current'] = goto

    def get_current_content(self):
        return self.content['text'][self.content['current']]

    def get_inline_status(self):
        return self.content['text'][self.content['current']]['inline']

    def set_inline_status(self, inline):
        content = self.get_current_content()
        content['inline'] = inline
        if inline:
            content['comment'] = (content['diff_chunk'] + '\n\n' +
                                  content['comment'])
        else:
            content['comment'] = content['comment'].replace(
                content['diff_chunk'], '').lstrip('\n')

    def get_status(self):
        """ Get the status, consisting of the current, total, percentage and
        number of comments. NOTE current is reported zero based and it is up
        to the GUI to change it for representation purposes
        """
        percentage =\
            (self.content['current'] + 1) * 100.0 / self.content['no_chunks']
        return {'current': self.content['current'],
                'total': self.content['no_chunks'],
                'percentage': percentage,
                'comments': self.__count_comments()}

    def update_comment(self, new_comment):
        self.content['text'][self.content['current']]['comment'] = new_comment

    def __count_comments(self):
        number = 0
        for element in self.content['text']:
            if element['comment'] != '':
                number = number + 1
        return number

    def set_bookmark(self):
        self.content['bookmark'] = self.content['current']

    def get_bookmark(self):
        return self.content['bookmark']

    def get_no_chunks(self):
        return int(self.content['no_chunks'])
