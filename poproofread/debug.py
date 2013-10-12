# -*- coding: utf-8 -*-
# pylint: disable-msg=W0603

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

# Setting
WIDTH = 76
# Global values
WRAP = -1

import sys


def level1(method):
    """ Level 1 debug messaging """
    def doit(*params, **kwargs):
        """ Decorator substitution function """
        global WRAP
        if params[0].level >= 1:
            WRAP = WRAP + 1
            output_debug_info(method, *params, **kwargs)
        try:
            return_value = method(*params, **kwargs)
        except:
            type_, value, traceback = sys.exc_info()
            raise type_, value, traceback.tb_next
        if params[0].level >= 1:
            output_return_value(return_value)
            WRAP = WRAP - 1
        return return_value
    return doit


def level2(method):
    """ Level 2 debug messaging """
    def doit(*params, **kwargs):
        """ Decorator substitution function """
        global WRAP
        if params[0].level >= 2:
            WRAP = WRAP + 1
            output_debug_info(method, *params, **kwargs)
        try:
            return_value = method(*params, **kwargs)
        except:
            type_, value, traceback = sys.exc_info()
            raise type_, value, traceback.tb_next
        if params[0].level >= 2:
            output_return_value(return_value)
            WRAP = WRAP - 1
        return return_value
    return doit


def level3(method):
    """ Level 3 debug messaging """
    def doit(*params, **kwargs):
        """ Decorator substitution function """
        global WRAP
        if params[0].level >= 3:
            WRAP = WRAP + 1
            output_debug_info(method, *params, **kwargs)
        try:
            return_value = method(*params, **kwargs)
        except:
            type_, value, traceback = sys.exc_info()
            raise type_, value, traceback.tb_next
        if params[0].level >= 3:
            output_return_value(return_value)
            WRAP = WRAP - 1
        return return_value
    return doit


def output_debug_info(method, *params, **kwargs):
    """ Output the methods debugging information """
    cls = str(params[0].__class__).lstrip('__main__.')
    meth = method.__name__
    # Generate parameter lists, 8 is the length of 'METHOD: '
    params_list = [format_string(str(param), 8, WRAP) for param in params[1:]]
    kwargs_list = [format_string('{0}={1}'.format(a, str(b)), 8, WRAP) for a, b
                   in kwargs.items()]
    # Generate output lines
    lines = []
    line = '{0}METHOD: {1}.{2}(self, '.format((' ' * WRAP), cls, meth)
    for arg in params_list + kwargs_list:
        # If adding the argument exceeds the max line length
        if len(line + arg + ', ') >= WIDTH:
            lines.append(line)
            line = ' ' * (8 + WRAP) + arg + ', '
        else:
            line += arg + ', '
    if line[-2:] == ', ':
        line = line[:-2]
    lines.append(line + ')')

    print '\n'.join(lines)


def output_return_value(value):
    """ Output the return value """
    print '{0}RETURN: {1}'.format((' ' * WRAP),
                                  format_string(value, 8, WRAP))


def format_string(obj, indent, wrap):
    """ Limit string representation length.

    Parameters:
    obj         object to turn into string representation
    indent      is the length of the section header like 'DEBUG: '
    wrap        number of levels the decorator wraps it self
    """
    limit = WIDTH - indent - wrap
    obj_str = repr(obj)
    #obj_str = obj_str.replace('\n', '\\n')
    if len(obj_str) > limit:
        # ' ... ' + 3 is the 8
        return obj_str[:limit - 8] + ' ... ' + obj_str[-3:]
    else:
        return obj_str
