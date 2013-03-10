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
    def doit(*params, **kwargs):
        """ Decorator substitution function """
        return_value = method(*params, **kwargs)
        if params[0].level >= 1:
            output_debug_info(method, return_value, *params, **kwargs)
        return return_value
    return doit


def level2(method):
    """ Level 2 debug messaging """
    def doit(*params, **kwargs):
        """ Decorator substitution function """
        return_value = method(*params, **kwargs)
        if params[0].level >= 2:
            output_debug_info(method, return_value, *params, **kwargs)
        return return_value
    return doit


def output_debug_info(method, ret, *params, **kwargs):
    """ Output the methods debugging information """
    cls = str(params[0].__class__).lstrip('__main__.')
    meth = method.__name__
    params_list = [format_string(str(param)) for param in params[1:]]
    kwargs_list = [format_string('{0}={1}'.format(a, str(b))) for a, b in\
                   kwargs.items()]
    args_string = ',\n      '.join(params_list + kwargs_list)
    if len(args_string) > 0:
        args_string = '\n      ' + args_string
    print 'DEBUG: {0}.{1}({2})\n  call returned {3}'.format(cls, meth,
        args_string, ret)


def format_string(obj):
    """ Limit string representation length """
    limit = 71  # 78 - (6 space indent and one "")") for the last argument
    obj_str = str(obj)
    if len(obj_str) > limit:
        return obj_str[0:limit - 8] + ' ... ' + obj_str[-3:]
    else:
        return obj_str
