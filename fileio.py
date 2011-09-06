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

import os

class FileIO():
    """ This class provides the file IO functionality 
    """

    def __init__(self, input_file, output_extension='.proofread'):
        """ Initiate variables and file states """
        self.input_file = input_file
        self.__check_input_file(self.input_file)

        self.output_file = self.input_file + output_extension
        self.output_exists = False
        self.__check_output_file(self.output_file)

    def __check_input_file(self, input_file):
        """ Check if input file can be read, otherwise raise exception """
        if not os.access(input_file, os.R_OK):
            raise SystemExit(1)

    def __check_output_file(self, output_file):
        """ Check if the output file exists, and if it can be read from and
        written to, otherwise throw exceptions.
        """
        if os.access(output_file, os.F_OK):
            self.output_exists = True
            if not os.access(output_file, os.W_OK):
                raise SystemExit(1)
            if not os.access(output_file, os.R_OK):
                raise SystemExit(1)
        else:
            dirname = os.path.dirname(output_file) if\
                os.path.dirname(output_file) != '' else '.'
            if not (os.access(dirname, os.W_OK) and
                    os.access(dirname, os.X_OK)):
                raise SystemExit(1)

    def read(self):
        """ Read files """
        
        with open(self.input_file) as f:
            content = str().join(f.readlines())

        # Make a list of dictionaries, taking the diff chunks by splitting
        # the file at '\n\n'
        self.chunks = [{'diff_chunk':cont, 'comment':''} for cont in
                       content.split('\n\n')]
        
        # If we are to continue old work
        if self.output_exists:
            with open(self.output_file) as f:
                content = str().join(f.readlines())
            
            # Split the content at '\n\n'
            self.already_done = content.split('\n\n')
            
            # Make a list of just the diff chunks
            diff_chunks = [e['diff_chunk'] for e in self.chunks]
            last_diff = ''
            gathering_comment = ''
            
            for e in self.already_done:
                # If the current chunk is a diff chunk ..
                if e in diff_chunks:
                    # .. not the first one ..
                    if last_diff != '':
                        # .. put the gathered comment in the apropriate
                        # dictionary
                        self.chunks[diff_chunks.index(last_diff)]['comment'] =\
                            gathering_comment
                    # Replace the last diff and reset the gathered comment
                    last_diff = e
                    gathering_comment = ''
                else:
                    # If the chunk was not a diff chunk, add it to the
                    # gathering comment
                    if gathering_comment == '':
                        gathering_comment = e
                    else:
                        gathering_comment += ('\n\n' + e)

            # Make sure we write the last comment even though we do not
            # encounter another real diff chunk after that
            if last_diff != '':
                self.chunks[diff_chunks.index(last_diff)]['comment'] =\
                    gathering_comment

        return self.chunks


    def write(self, content):
        """ Write all the comments to file, if there is something to write """

        # First check whether there is actually anything to write
        if [e['comment'] for e in content].count('') == len(content):
            print "no comment"
            return
        
        f = open(self.output_file, 'w')
        
        # Write the comments
        first = True
        for chunk in content:
            if chunk['comment'] != '':
                if not first:
                    f.write('\n\n')
                else:
                    first = False
                f.write(chunk['diff_chunk'])
                f.write('\n\n')
                f.write(chunk['comment'])
        f.write('\n')

        f.close()

        return True
