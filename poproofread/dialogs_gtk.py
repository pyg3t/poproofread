# -*- coding: utf-8 -*-

"""
poproofread-gtk.py
This file is a part of PoProofRead.

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

import os
import pygtk
pygtk.require('2.0')
import gtk


class Dialog:
    def __init__(self, object_name):
        """ Abstract class for all dialogs """

        # Form the paths for all the dialogs
        guidir = os.path.dirname(__file__) + os.sep + 'gui' + os.sep
        paths = {'inf_dia_ok': guidir + 'info_dialog_ok.glade'}

        # Read the layout xml
        with open(paths[object_name]) as xmlfile:
            layout_xml = xmlfile.read()

        # Form the dialog and assign it to a convenient name
        self.builder = gtk.Builder()
        self.builder.add_from_string(layout_xml)
        self.dialog = self.builder.get_object(object_name)


class ErrorDialogOK(Dialog):
    """ Information dialog with on a OK button """
    def __init__(self, text, sec_text):
        Dialog.__init__(self, 'inf_dia_ok')
        self.dialog.set_property('text', text)
        self.dialog.set_property('secondary-text', sec_text)
        # This can be used to set the type of message: gtk.MESSAGE_INFO,
        # gtk.MESSAGE_WARNING, gtk.MESSAGE_QUESTION or gtk.MESSAGE_ERROR.
        self.dialog.set_property('message-type', gtk.MESSAGE_ERROR)

    def run(self):
        ans = self.builder.get_object('inf_dia_ok').run()
        self.builder.get_object('inf_dia_ok').destroy()
        return ans

class WarningDialogOK(Dialog):
    """ Information dialog with on a OK button """
    def __init__(self, text, sec_text):
        Dialog.__init__(self, 'inf_dia_ok')
        self.dialog.set_property('text', text)
        self.dialog.set_property('secondary-text', sec_text)
        # This can be used to set the type of message: gtk.MESSAGE_INFO,
        # gtk.MESSAGE_WARNING, gtk.MESSAGE_QUESTION or gtk.MESSAGE_ERROR.
        self.dialog.set_property('message-type', gtk.MESSAGE_WARNING)

    def run(self):
        ans = self.builder.get_object('inf_dia_ok').run()
        self.builder.get_object('inf_dia_ok').destroy()
        return ans
