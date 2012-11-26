# -*- coding: utf-8 -*-

"""
debug.py
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


def level1(method):
    """ Level 1 debug messaging """
    def doit(*args):
        """ Decorator substitution function """
        if args[0].level >= 1:
            print 'DEBUG:', method.__name__, list(args)[1:]
        return method(*args)
    return doit


def level2(method):
    """ Level 2 debug messaging """
    def doit(*args):
        """ Decorator substitution function """
        if args[0].level >= 2:
            print 'DEBUG:', method.__name__, list(args)[1:]
        return method(*args)
    return doit
