"""
poproofread -- A podiff proofreader for the terminal
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

from fileio import FileIO

class PoProofRead():
    """ Main functionality for poproofread """

    def __init__(self):
        active = False
        self.file = None
        self.current = None
        self.content = None

    def open(self, filename):
        self.file = FileIO(filename)
        self.content = self.file.read()
        self.current = 0

    def save(self):
        self.file.write(self.content)

    def move(self, amount=None, goto=None):
        if amount:
            self.current = self.current + amount
            # There has got to be a more pythonic way of doing this
            if self.current < 0:
                self.current = 0
            if self.current >= len(self.content):
                self.current = len(self.content)-1

    def get_current_content(self):
        return self.content[self.current]

    def get_status(self):
        percentage = (self.current+1)*100.0/len(self.content)
        print type(self.current), type(len(self.content))
        return {'current': self.current+1, 'total': len(self.content),
                'percentage': '%.0f' % percentage,
                'comments': self.__count_comments()}
    
    def update_comment(self, new_comment):
        self.content[self.current]['comment'] = new_comment

    def __count_comments(self):
        number = 0
        for element in self.content:
            if element['comment'] != '':
                number = number + 1
        return number
