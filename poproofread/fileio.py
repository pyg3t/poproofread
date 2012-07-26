# -*- coding: utf-8 -*-

"""
fileio.py
This file is a part of PoProofRead

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

import os
import json
import codecs
import re
import StringIO
from dialogs_gtk import EncodingDialogOK, QuestionWarningDialog
from custom_exceptions import FileError, FileWarning, UnhandledException


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
                # get warnings
                content = self.__read_new(input_file)
                actual_file = input_file + '.ppr'
                print 'Loaded new diff'
        return (content, actual_file, warnings)

    def __read_ppr(self, input_file):
        """ Read content from .ppr file """
        self._set_new_file_location(input_file, existing=True, ppr=True)

        with open(input_file) as file_:
            return json.loads(file_.read())

    def __read_new(self, input_file):
        """ Read content from new file """
        self._set_new_file_location(input_file, existing=False, ppr=False)

        if not os.access(input_file, os.F_OK):
            raise FileError(input_file, 'The file does not exist.')
        if not os.access(input_file, os.R_OK):
            raise FileError(input_file, 'The file is not readable.')

        encoding = self.__detect_character_encoding(input_file)

        with codecs.open(input_file, encoding=encoding) as file_:
            diff_chunks = file_.read().split('\n\n')

        diff_list = [{'diff_chunk': diff, 'comment': '', 'inline': False}
                     for diff in diff_chunks]

        return {'text': diff_list, 'encoding': encoding, 'bookmark': None,
                'current': 0, 'no_chunks': len(diff_list)}

    def check_and_set_new_file_location(self, filename):
        """ Check if file exists and the set new file locations """
        if os.path.splitext(filename)[1] != '.ppr':
            filename += '.ppr'
        outfile = filename + '.out'

        existing = False
        if os.access(filename, os.F_OK) or os.access(filename, os.F_OK):
            if os.access(filename, os.F_OK):
                existing = True
            ans = QuestionWarningDialog('File exists, overwrite?',
                    ('One of the files:\n{0}\n{1}\nalready exist. Do you ' +
                    'wish to overwrite it and loose the current content of ' +
                    'the file?').format(filename, outfile)
                ).run()

        if not existing:
            self._set_new_file_location(filename, existing=False, ppr=True)
        elif existing and ans:
            self._set_new_file_location(filename, existing=True, ppr=True)
        else:
            return False, None
        return True, filename

    def _set_new_file_location(self, filename, existing, ppr):
        """ Set new file locations and check if they are usable """
        if ppr:
            self.ppr_file = filename
        else:
            self.ppr_file = filename + '.ppr'
        self.out_file = self.ppr_file + '.out'
        self.__check_ppr_and_out_file(self.ppr_file, self.out_file, existing)

    def __check_ppr_and_out_file(self, ppr_file, out_file, existing):
        """ Check file permissions """
        # Error messages on failed file tests
        err_msgs = {
            os.R_OK: 'The file is not readable.',
            os.W_OK: 'The file is not writeable.',
            os.F_OK: 'The file does not exist.',
            'dummy': 'The file cannot be created.'
        }
        if existing:  # If we are told the file exists
            for test in [os.F_OK, os.R_OK, os.W_OK]:  # check exists, r & w
                if not os.access(ppr_file, test):
                    raise FileError(ppr_file, err_msgs[test])
        else:  # if told the file does not exist
            if os.access(ppr_file, os.F_OK):  # check if it does anyway
                for test in [os.R_OK, os.W_OK]:  # check r & w
                    if not os.access(ppr_file, test):
                        raise FileError(ppr_file, err_msgs[test])
            else:  # if it does not exist anyway, check if dirname
                dirname = os.path.dirname(ppr_file)\
                    if os.path.dirname(ppr_file) != '' else '.'
                # has wx permission so the file can be created
                if not (os.access(dirname, os.W_OK) and
                        os.access(dirname, os.X_OK)):
                    raise FileError(ppr_file, err_msgs[3][1])

        # Out file tests
        if os.access(out_file, os.F_OK):
            if not os.access(self.out_file, os.W_OK):
                raise FileError(out_file, 'The file is not writeable.')
        else:
            dirname = os.path.dirname(out_file)\
                if os.path.dirname(out_file) != '' else '.'
            if not (os.access(dirname, os.W_OK) and
                    os.access(dirname, os.X_OK)):
                raise FileError(out_file, 'The file cannot be created.')

    def __detect_character_encoding(self, input_file):
        """ Detect the character encoding of a new file """
        # First try to read it from a po type file
        # Search for diff type (+- ) line and charset in Content-Type line
        charset_pattern = r'^(.*)"Content-Type:.*charset=([a-zA-Z0-9-]*).*$'
        with open(input_file) as file_:
            for line in file_.readlines():
                search = re.search(charset_pattern, line)
                try:
                    # A diff has a character before #Content-Type...
                    if len(search.group(1)) > 0:
                        if search.group(1) in ['+', ' ']:
                            return search.group(2)
                    # a reular po-file does not
                    else:
                        return search.group(2)
                except AttributeError:
                    pass

        # Try to detect with chardet
        try:
            import chardet
            with open(input_file, "r") as file_:
                rawdata = file_.read()
                detected = chardet.detect(rawdata)
        except ImportError:
            detected = [None, None]

        text = ('It was not possible to read the encoding of this file '
                'directly from the content. Therefore, please select an '
                'encoding below or press "Cancel" to abort loading the '
                'file.\n\nAfter loading the file please write a test '
                'comment that contains the characters that are special '
                'for this encoding and test that it can be saved and that '
                'the output looks correct.')
        enc_dialog = EncodingDialogOK(text, detected['encoding'],
                                      detected['confidence'])
        selected_enc = enc_dialog.run()
        aborted_text = ('Loading of the file was aborted.')
        if selected_enc is None:
            raise FileError(input_file, aborted_text)
        while True:
            try:
                rawdata.decode(selected_enc)
                enc_dialog.destroy()
                return selected_enc
            except UnicodeDecodeError:
                text = ('The selected encoding: {0}\n'
                        'could not decode the file content. Please select '
                        'another decoding to try again or press "Cancel" to '
                        'abort loading the file.\n\nAfter loading the file '
                        'please write a test comment that contains the '
                        'characters that are special for this encoding and '
                        'test that it can be saved and that the output '
                        'looks correct.').format(selected_enc)
                enc_dialog.set_text(text)
                selected_enc = enc_dialog.run()
                if selected_enc is None:
                    raise FileError(input_file, aborted_text)

    def write(self, content, clipboard=False):
        """ Write content to ppr and out file """
        self.__write_to_ppr(content)
        charset_warning, text = \
            self.__write_to_out(content, clipboard=clipboard)
        return charset_warning, text

    def __write_to_ppr(self, content):
        """ Write json representation of content to .ppr file """
        with open(self.ppr_file, 'w') as file_:
            file_.write(json.dumps(content))

    def __write_to_out(self, content, override_encoding=False,
                       clipboard=False):
        """ Write out file

        Returns warning or None and text or None"""
        encoding = 'utf-8' if override_encoding else content['encoding']
        if clipboard:
            file_ = StringIO.StringIO()
        else:
            file_ = codecs.open(self.out_file, encoding=encoding, mode='w')

        for comment in content['text']:
            if comment['comment'] != '':
                try:
                    if not comment['inline']:
                        file_.write(comment['diff_chunk'] + '\n\n')
                    file_.write(comment['comment'] + '\n\n')
                except UnicodeEncodeError:
                    if not override_encoding:
                        text = self.__write_to_out(content,
                                                   override_encoding=True)[1]
                    else:
                        file_.close()
                        raise UnhandledException('Char set save loop')
                    warning = ('It was not possible to save the content '
                               'to the .ppr.out-file in the detected '
                               'encoding "{0}". Falling back to "utf-8" '
                               'for this file.\n\nPlease check if the '
                               'output looks correct!'
                               '').format(content['encoding'])
                    file_.close()
                    return FileWarning(self.out_file, warning), text

        if clipboard:
            text = file_.getvalue()
            file_.close()
        else:
            text = None

        return None, text
