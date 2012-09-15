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

import json
import os
import StringIO
from time import strftime
from fileio import FileIO


class PoProofRead():
    """ Main functionality for PoProofRead. This class contains and controls
    all of the functionality of PoProodRead except for the GUI. All index for
    the diff part list are zero based from this class and downwards.
    """

    def __init__(self):
        self.fileio = FileIO()
        self.active = False
        self.content = None

    ##############################
    ### "File operation" functions
    def open(self, filename):
        """ Open a file """
        text, enc, actual_file, warnings, ppr = self.fileio.read(filename)
        # The next line will only be executed if open was succesfull, because
        # errors will raise exceptions
        self.active = True
        if ppr:
            self.content = json.loads(text)
        else:
            self.content = self._parse_text(text, enc)
        return actual_file, warnings

    def import_from_text(self, text):
        """ Import text as the diff to be proofread """
        self.content = self._parse_text(text)
        tmpfilename = strftime('poproofread-{0}-%Y-%m-%d_%H:%M:%S').\
            format(os.getlogin())
        filename = \
            self.fileio.check_and_set_new_file_location(tmpfilename, True)[1]
        self.active = True
        return filename

    def close(self):
        """ Close or reset functionality """
        self.fileio.__init__()
        self.active = False
        self.content = None

    def save(self, clipboard=False):
        """ Save. If 'clipboard' the output is returned in 'text'

        Return  : returns warning, text
        """
        #if self.fileio.get_file_locations() == (None, None):
        #    return None, ''
        text = self._create_output_text()
        charset_warning = None
        if not clipboard:
            charset_warning = self.fileio.write(json.dumps(self.content),
                                                text,
                                                self.content['encoding'])
            if charset_warning is not None:
                self.content['encoding'] = 'utf-8'
        return charset_warning, text

    def set_new_save_location(self, filename):
        """ Set new save location. For "Save as" functionality """
        ok_to_save, actual_filename = \
            self.fileio.check_and_set_new_file_location(filename)
        return ok_to_save, actual_filename

    #############################
    ### PoProofRead-ing functions
    def move(self, amount=None, goto=None):
        """ Move to a different diff part. Either by 'amount' or to 'goto' """
        if amount != None:
            requested = self.content['current'] + amount
        elif goto != None:
            requested = goto
            if goto < 0:
                requested = self.content['no_chunks'] + goto
        # Coerce in range
        self.content['current'] = \
            max(0, min(requested, self.content['no_chunks'] - 1))

    def get_current_content(self):
        """ Return the current part """
        return self.content['text'][self.content['current']]

    def get_inline_status(self):
        """ Return the inline status of the current diff part """
        return self.content['text'][self.content['current']]['inline']

    def set_inline_status(self, inline):
        """ Set the inline status of the diff part and edit the comment
        accordingly.
        """
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
        percentage = \
            (self.content['current'] + 1) * 100.0 / self.content['no_chunks']
        return {'current': self.content['current'],
                'total': self.content['no_chunks'],
                'percentage': percentage,
                'comments': self.__count_comments()}

    def update_comment(self, new_comment):
        """ Update the comment for the current diff part """
        self.content['text'][self.content['current']]['comment'] = new_comment

    def set_bookmark(self):
        """ Set the bookmark to the current diff part """
        self.content['bookmark'] = self.content['current']

    def get_bookmark(self):
        """ Return the bookmark """
        return self.content['bookmark']

    def get_no_chunks(self):
        """ Return the number of diff parts """
        return self.content['no_chunks']

    #####################
    ### Utility functions
    def __count_comments(self):
        """ Return the number of comments in the proofreading """
        number = 0
        for element in self.content['text']:
            if element['comment'] != '':
                number += 1
        return number

    @staticmethod
    def _parse_text(text, encoding='utf-8'):
        """ Parse text and return the default content data structure
        Keyword arguments:
        encoding (str)  The encoding of the original content
        text (str)      The text to be parsed
        Return          Returns the default data structure dictionary
        """
        diff_chunks = text.split('\n\n')
        diff_chunks_crlf = text.split('\r\n\r\n')
        # Check for CLRF line endings
        if len(diff_chunks_crlf) > len(diff_chunks):
            # .. and remove them in the output<
            diff_chunks = [chunk.replace('\r\n', '\n')
                           for chunk in diff_chunks_crlf]

        diff_list = [{'diff_chunk': diff, 'comment': '', 'inline': False}
                    for diff in diff_chunks]
        # This dictionary represents the default data structure version 1
        default_datastructure = {
            'text': diff_list,
            'encoding': encoding,
            'bookmark': None,
            'current': 0,
            'no_chunks': len(diff_list)
        }
        return default_datastructure

    def _create_output_text(self):
        """ Create the output text in a StringIO buffer """
        file_ = StringIO.StringIO()
        for comment in self.content['text']:
            if comment['comment'] != '':
                if not comment['inline']:
                    file_.write(comment['diff_chunk'] + '\n\n')
                file_.write(comment['comment'] + '\n\n')

        text = file_.getvalue()
        file_.close()
        return text
