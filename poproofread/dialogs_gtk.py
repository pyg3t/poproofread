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
import encodings
import pkgutil
import pygtk
pygtk.require('2.0')
import gtk


class Dialog:
    def __init__(self, object_name):
        """ Abstract class for all dialogs """

        # Form the paths for all the dialogs
        guidir = os.path.dirname(__file__) + os.sep + 'gui' + os.sep
        paths = {'inf_dia_ok': guidir + 'info_dialog_ok.glade',
                 'enc_dia_ok': guidir + 'encoding_selection_dialog.glade'}

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


class EncodingDialogOK(Dialog):
    """ Encoding selection dialog """

    def __init__(self, text, autodetected=None, autodetect_confidence=0):
        Dialog.__init__(self, 'enc_dia_ok')
        self.autodetected = autodetected
        self.set_text(text)
        self.builder.get_object('label_description').set_line_wrap(True)

        # Fill out the encoding combobox
        self.combo = self.builder.get_object('combobox_enc')
        # See if there is an easier way to do this, and make sure that these
        # encodings are only text encodings
        false_positives = set(["aliases", "base64_codec", "bz2_codec",
                               "hex_codec", "idna", "mbcs", "palmos",
                               "punycode", "quopri_codec",
                               "raw_unicode_escape", "rot_13", "string_escape",
                               "undefined", "unicode_escape",
                               "unicode_internal", "uu_codec", "zlib_codec"])

        encs = set(name for imp, name, ispkg in
                   pkgutil.iter_modules(encodings.__path__) if not ispkg)
        encs.difference_update(false_positives)
        encs = list(encs)
        encs.sort()
        for enc in encs:
            self.combo.append_text(enc)
        self.combo.set_active(0)

        # Fill out the autodetect option or deactivate
        if autodetected is None:
            self.builder.get_object('radiobutton_autodetect').\
                set_sensitive(False)
        else:
            self.builder.get_object('label_autodetect').set_text(
                '{0} with {1:.0f}% confidence'.format(
                    autodetected, autodetect_confidence * 100))
        self.dialog = self.builder.get_object('dialog_encodings')
        self.builder.connect_signals(self)

    def run(self):
        ans = self.dialog.run()
        if ans == -5:
            radio_group = self.builder.get_object('radiobutton_default')\
                .get_group()
            radio_active = [r for r in radio_group if r.get_active()][0]
            if radio_active == self.builder.get_object('radiobutton_default'):
                ret = 'utf_8'
            elif radio_active == self.builder.get_object(
                'radiobutton_autodetect'):
                ret = self.autodetected
            else:
                model = self.combo.get_model()
                ret = model[self.combo.get_active()][0]
        else:
            self.destroy()
            ret = None
        return ret

    def destroy(self):
        self.dialog.destroy()

    def set_text(self, text):
        self.builder.get_object('label_description').set_text(text)

    def on_combobox_enc_changed(self, widget):
        """ Call back that actives the manual radio button, when the manuel
        selection combobox has been changed
        """
        self.builder.get_object('radiobutton_manual').set_active(2)

    def on_label_description_size_allocate(self, widget, size):
        """ Hack to get label text wrapping to work """
        widget.set_size_request(size.width, -1)
