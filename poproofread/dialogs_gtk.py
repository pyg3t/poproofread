# -*- coding: utf-8 -*-
# pylint: disable-msg=W0613,R0903,R0201

"""
poproofread-Gtk.py
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

import os
import encodings
import pkgutil
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import __init__


# FIXME
# THIS IS A HACK. Gtk3 warns about dialogs not being transient of modal, untill
# I figure out if I should ultimately fix this by combining all glade into one
# file I will just set the parent globally instead of passing it as argument
# everywhere
PARENT=None
def set_parent(parent):
    global PARENT
    PARENT = parent


class Dialog:
    """ Abstract class for all dialogs that loads the gui and assigns the
    dialog to a variable
    """
    def __init__(self, object_name):
        # Form the paths for all the dialogs
        guidir = os.path.join(os.path.dirname(__file__), 'gui')

        def tot_dir(glade_file):
            """ Convinience function to form join glade file paths """
            return os.path.join(guidir, glade_file)
        paths = {
            'mes_dia_ok': tot_dir('message_dialog_ok.glade'),
            'enc_dia_ok': tot_dir('encoding_selection_dialog.glade'),
            'save_as_dia': tot_dir('file_chooser_dialog_save_as.glade'),
            'question_dia': tot_dir('question_dialog.glade'),
            'open_dia': tot_dir('file_chooser_dialog_open.glade'),
            'about_dia': tot_dir('about_dialog.glade'),
            'jump_to_dia': tot_dir('jump_to_dialog.glade')
            }

        # Read the layout xml
        with open(paths[object_name]) as xmlfile:
            layout_xml = xmlfile.read()

        # Form the dialog and assign it to a convenient name
        self.builder = Gtk.Builder()
        self.builder.add_from_string(layout_xml)
        self.dialog = self.builder.get_object(object_name)
        self.dialog.set_transient_for(PARENT)


class MessageDialog(Dialog):
    """ Abstract class for all message dialogs """
    def __init__(self, message_dialog_type, text, sec_text, question=False):
        if question:
            Dialog.__init__(self, 'question_dia')
        else:
            Dialog.__init__(self, 'mes_dia_ok')
        self.dialog.set_property('text', text)
        self.dialog.set_property('secondary-text', sec_text)
        # This can be used to set the type of message: Gtk.MessageType.INFO,
        # Gtk.MessageType.WARNING, Gtk.MessageType.QUESTION or Gtk.MessageType.ERROR.
        self.dialog.set_property('message-type', message_dialog_type)

    def run(self):
        """ Run the dialog and get an answer """
        ans = self.dialog.run()
        self.dialog.destroy()
        return ans


class ErrorDialogOK(MessageDialog):
    """ Error dialog with on a OK button """
    def __init__(self, text, sec_text):
        MessageDialog.__init__(self, Gtk.MessageType.ERROR, text, sec_text)


class WarningDialogOK(MessageDialog):
    """ Information dialog with on a OK button """
    def __init__(self, text, sec_text):
        MessageDialog.__init__(self, Gtk.MessageType.WARNING, text, sec_text)


class QuestionWarningDialog(MessageDialog):
    """ Question dialog with ok and cancel buttons """
    def __init__(self, text, sec_text):
        MessageDialog.__init__(self, Gtk.MessageType.WARNING, text, sec_text,
            question=True)

    def run(self):
        ret = False
        if MessageDialog.run(self) == -5:
            ret = True
        return ret


class EncodingDialogOK(Dialog):
    """ Encoding selection dialog """
    def __init__(self, text, autodetected=None, autodetect_confidence=0):
        Dialog.__init__(self, 'enc_dia_ok')
        self.autodetected = autodetected
        self.set_text(text)
        self.builder.get_object('label_desc').set_line_wrap(True)

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
        """ Run the dialog and get an answer """
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
        """ Destroy the dialog """
        self.dialog.destroy()

    def set_text(self, text):
        """ Set the text in the main dialog message label """
        self.builder.get_object('label_desc').set_text(text)

    def on_combobox_enc_changed(self, widget):
        """ Call back that actives the manual radio button, when the manuel
        selection combobox has been changed
        """
        self.builder.get_object('radiobutton_manual').set_active(2)

    def on_label_desc_size_allocate(self, widget, size):
        """ Hack to get label text wrapping to work """
        widget.set_size_request(size.width, -1)


class SaveAsDialog(Dialog):
    """ Save as dialog """
    def __init__(self, current_dir):
        Dialog.__init__(self, 'save_as_dia')
        self.dialog.set_current_folder(current_dir)
        file_filter = self.builder.get_object('save_as_file_filter')
        file_filter.add_pattern('*.ppr')

    def run(self):
        """ Run the dialog and return the filename. None is returned of no
        file name was selected. The self.dialog.get_filename() method itself
        return None in case of Cancel, window destroy of Ok without a filename
        """
        self.dialog.run()
        filename = self.dialog.get_filename()
        current_dir = self.dialog.get_current_folder()
        self.dialog.destroy()
        return filename, current_dir


class OpenDialog(Dialog):
    """ Open dialog """
    def __init__(self, current_dir):
        Dialog.__init__(self, 'open_dia')
        self.dialog.set_current_folder(current_dir)

    def run(self):
        """ Run the dialog and return the filename and the current folder """
        ans = self.dialog.run()
        filename = self.dialog.get_filename()
        while os.path.isdir(filename) and ans == 0:
            self.dialog.set_current_folder(filename)
            ans = self.dialog.run()
            filename = self.dialog.get_filename()
        if ans == 0:
            current_dir = self.dialog.get_current_folder()
        else:
            current_dir = filename = None
        self.dialog.destroy()
        return filename, current_dir


class AboutDialog(Dialog):
    """ About dialog """
    def __init__(self):
        Dialog.__init__(self, 'about_dia')
        self.dialog.set_version(__init__.__version__)

    def run(self):
        """ Run the dialog """
        self.dialog.run()
        self.dialog.destroy()


class JumpToDialog(Dialog):
    """ Jump to dialog """
    def __init__(self, min_, max_):
        Dialog.__init__(self, 'jump_to_dia')
        self.spinbtn = self.builder.get_object('spinbtn_jump_to')
        self.spinbtn.set_range(min_, max_)

    def run(self):
        """ Run the dialog and return the result """
        ans = self.dialog.run()
        ret = None
        if ans == 0:
            ret = self.spinbtn.get_value_as_int()
        self.dialog.destroy()
        return ret
