#!/usr/bin/env python
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
import sys
try:
    import argparse
except ImportError:
    import optparse
import pygtk
pygtk.require('2.0')
import pango
import gtk
import glib
from core import PoProofRead
from settings import Settings
from custom_exceptions import FileError
from dialogs_gtk import ErrorDialogOK, WarningDialogOK
import __init__


class PoProofReadGtkGUI:

    def __init__(self):
        # Get settings
        self.settings = Settings()

        # Initiate core
        self.ppr = PoProofRead()

        # Load gui and connect signals
        self.builder = gtk.Builder()
        moduledir = os.path.dirname(__file__)
        self.gladefile = moduledir + os.sep + 'gui/poproofread_gtk_gui.glade'
        self.iconfile = moduledir + os.sep + 'graphics/192.png'

        try:
            self.builder.add_from_file(self.gladefile)
        except glib.GError as error:
            print "Your gtk version is not new enough:\n", error
            sys.exit(1)

        self.builder.connect_signals(self)
        self.builder.get_object('poproofread').\
            set_icon_from_file(self.iconfile)

        self.filech = self.get_object('filechooserdialog_open')

        self.labels = {
            'lab_current_pos': self.builder.get_object("lab_current_pos"),
            'lab_total': self.builder.get_object("lab_total"),
            'lab_percentage': self.builder.get_object("lab_percentage"),
            'lab_comments': self.builder.get_object("lab_comments"),
            }

        # tb short for textbuffer
        self.tb_diff, self.tb_comment = gtk.TextBuffer(), gtk.TextBuffer()
        self.builder.get_object('textview_diff').set_buffer(self.tb_diff)
        self.builder.get_object('textview_comment').set_buffer(self.tb_comment)
        self.clipboard = gtk.Clipboard()

        # Color the background of the diff window grey
        self.builder.get_object('textview_diff').modify_base(
            self.builder.get_object('textview_diff').get_state(),
            gtk.gdk.Color(red=58000, green=58000, blue=58000))

        # Assign commonly used widgets local variable names
        self.sw1 = self.builder.get_object('scrolledwindow1')
        self.sw2 = self.builder.get_object('scrolledwindow2')
        self.vbox1 = self.builder.get_object('vbox1')
        self.sep1 = self.builder.get_object('hseparator1')

        self.settings_to_gui()
        self.reset_gui()

    # Mandatory gtk windown handling
    def on_window_destroy(self, widget):
        self.on_mnu_quit(widget)

    ### GUI widgets
    # Buttons
    def on_btn_set_bookmark(self, widget):
        self.ppr.set_bookmark()
        self.update_bookmark()

    def on_btn_jump_to_bookmark(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=self.ppr.get_bookmark())
        self.update_gui()

    def on_checkbutton_inline(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.set_inline_status(widget.get_active())
        self.update_gui()

    def on_btn_first(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=0)
        self.update_gui()

    def on_btn_previous(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.move(amount=-1)
        self.update_gui()

    def on_btn_next(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.move(amount=1)
        self.update_gui()

    def on_btn_last(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=-1)
        self.update_gui()

    def on_btn_jump_to(self, widget):
        self.get_object('dialog_jump_to').show()
        self.get_object('spinbtn_jump_to')\
            .set_range(1, self.ppr.get_no_chunks())
        # MAKE THE NUMBER SELECTED

    def on_jump_to_ok(self, widget):
        value = self.get_object('spinbtn_jump_to').get_value_as_int()
        self.get_object('dialog_jump_to').hide()
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=value - 1)
        self.update_gui()

    def on_jump_to_cancel(self, widget):
        self.get_object('dialog_jump_to').hide()

    ### GUI widgets ##########################################################
    # Menus
    # File menu
    def on_mnu_open(self, widget):
        # Reinitialize dialog in case it was destroyed
        self.builder.add_objects_from_file(self.gladefile,
                                           ['filechooserdialog_open'])
        self.builder.connect_signals(self)
        self.filech = self.get_object('filechooserdialog_open')
        # Change current directory
        if os.path.isdir(self.settings['current_dir']):
            self.filech.set_current_folder(self.settings['current_dir'])

        self.filech.show()

    def on_filechooser(self, widget):
        filename = self.filech.get_filename()
        if os.path.isdir(filename):
            self.filech.set_current_folder(filename)
        else:
            self.settings['current_dir'] = self.filech.get_current_folder()
            self.filech.destroy()
            self.open_file(filename)

    def on_filechooser_cancel(self, widget):
        self.filech.destroy()

    def on_mnu_save(self, widget):
        if self.ppr.active:
            if not self.check_for_new_comment_and_save_it():
                self.ppr.save()

    def on_mnu_close(self, widget):
        if self.ppr.active:
            self.check_for_new_comment_and_save_it()
            self.ppr.close()
            self.reset_gui()

    def on_mnu_quit(self, widget):
        if self.ppr.active:
            self.check_for_new_comment_and_save_it()
            self.ppr.save()
        self.settings.write()
        gtk.main_quit()

    ########################################
    # Edit menu
    def on_mnu_copy(self, widget):
        if not self.ppr.active:
            return
        tb_with_selection = self.get_textbuffer_with_selection()
        if tb_with_selection is not None:
            tb_with_selection.copy_clipboard(self.clipboard)

    def on_mnu_paste(self, widget):
        if not self.ppr.active:
            return
        self.tb_comment.paste_clipboard(self.clipboard, None, True)

    def on_mnu_cut(self, widget):
        if not self.ppr.active:
            return
        if self.get_textbuffer_with_selection() is self.tb_comment:
            self.tb_comment.cut_clipboard(self.clipboard, True)

    def on_mnu_delete(self, widget):
        if not self.ppr.active:
            return
        if self.get_textbuffer_with_selection() is self.tb_comment:
            self.tb_comment.delete_selection(True, True)

    ########################################
    # Help menu
    def on_mnu_about(self, widget):
        # Reinitialize the dialog in case it has been destroyed
        self.builder.add_objects_from_file(self.gladefile,
                                           ['aboutdialog'])
        # Set version
        self.get_object('aboutdialog').set_version(__init__.__version__)
        # -4 and -6 equals destroy window and close button
        if self.get_object('aboutdialog').run() in [-4, -6]:
            self.get_object('aboutdialog').destroy()

    ### General functions ####################################################
    def get_object(self, name):
        return self.builder.get_object(name)

    def write_to_textbuffer(self, textbuffer, text):
        """ Deletes anything in textbuffer and replaces it with text """
        startiter, enditer = textbuffer.get_bounds()
        textbuffer.delete(startiter, enditer)
        textbuffer.insert(startiter, text)

    def read_comment(self):
        """ Return the content of the comment window """
        startiter, enditer = self.tb_comment.get_bounds()
        return self.tb_comment.get_text(startiter, enditer)

    def settings_to_gui(self):
        pangofont = pango.FontDescription('Monospace ' +
                                          str(self.settings['font_size']))
        self.get_object('textview_diff').modify_font(pangofont)
        self.get_object('textview_comment').modify_font(pangofont)

    def reset_gui(self):
        welcome = ('Welcome to PoProofRead version {0}\n\n'
                   'To use PoProofRead simply load the podiff you wish to '
                   'proofread, move through the file with PageUp and PageDown '
                   'and when you wish to make a comment, just start typing. '
                   'The program will auto-save everytime you move away from a '
                   'new comment.\n\n'
                   'Keyboard shortcuts:\n'
                   'Previous part  : PageUp     Next part     : PageDown\n'
                   'First part     : Ctrl-Home  Last          : Ctrl-End\n\n'
                   'Toggle inline commenting: Ctrl-i\n'
                   'Set bookmark   : Ctrl-b     Go to bookmark: Ctrl-g\n'
                   'Jump to part # : Ctrl-j\n\n'
                   'Open file      : Ctrl-o     Save file     : Ctrl-s\n'
                   'Close file     : Ctrl-w     Quit          : Ctrl-q\n'
                   'Copy           : Ctrl-c     Cut           : Ctrl-x\n'
                   'Paste          : Ctrl-v     Delete        : Delete\n\n'
                   'If in doubt, just move the mouse over the button and the '
                   'keyboard shortcut will be in the tool tip.')\
                   .format(__init__.__version__)
        self.write_to_textbuffer(self.tb_diff, welcome)
        self.write_to_textbuffer(self.tb_comment, '')
        for label in self.labels.values():
            label.set_text('-')
        self.get_object('hbox_buttons').set_sensitive(False)
        self.get_object('hbox_statusline').set_sensitive(False)
        self.get_object('poproofread').set_title('PoProofRead')
        self.update_inline_gui(False)

    def update_gui(self):
        if not self.ppr.active:
            return

        # Read inline status from ppr and update checkbutton accordingly
        inline = self.ppr.get_inline_status()
        self.get_object('checkbutton_inline').handler_block_by_func(
            self.on_checkbutton_inline)
        self.get_object('checkbutton_inline').set_active(inline)
        self.get_object('checkbutton_inline').handler_unblock_by_func(
            self.on_checkbutton_inline)

        self.update_inline_gui(inline)

        # Update text content
        content = self.ppr.get_current_content()
        self.write_to_textbuffer(self.tb_diff, content['diff_chunk'])
        self.write_to_textbuffer(self.tb_comment, content['comment'])
        # Move cursor to end of comment
        # get_bounds returns (startiter, enditer)
        enditer = self.tb_comment.get_bounds()[1]
        self.get_object('textview_comment').grab_focus()
        self.tb_comment.place_cursor(enditer)
        mark = self.tb_comment.create_mark(None, enditer)
        self.get_object('textview_comment').scroll_mark_onscreen(mark)

        # Get status and update sensitivity of buttons and the statusline
        status = self.ppr.get_status()
        self.update_status_line(str(status['current'] + 1),
                                str(status['total']),
                                '%.0f%%' % status['percentage'],
                                str(status['comments']))
        if status['current'] == 0:
            self.set_sensitive_nav_buttons([False, False, True, True])
        elif status['current'] == status['total'] - 1:
            self.set_sensitive_nav_buttons([True, True, False, False])
        else:
            self.set_sensitive_nav_buttons([True, True, True, True])

        self.tb_comment.set_modified(False)

        self.update_bookmark()

    def update_inline_gui(self, inline):
        # Update GUI according to inline status
        par2 = self.vbox1.query_child_packing(self.sw2)
        if inline and self.vbox1.children().count(self.sw1) == 1:
            # If inline and not already in inline layout ...
            self.vbox1.remove(self.sep1)
            self.vbox1.remove(self.sw1)
            self.sw2.set_size_request(-1, -1)
            self.vbox1.set_child_packing(self.sw2, True, *par2[1:])
        elif not inline and self.vbox1.children().count(self.sw1) == 0:
            # ... and vice versa
            self.vbox1.pack_start(self.sw1, True, True, 0)
            self.vbox1.reorder_child(self.sw1, 2)
            self.vbox1.pack_start(self.sep1, False, True, 0)
            self.vbox1.reorder_child(self.sep1, 3)
            self.sw2.set_size_request(-1, 100)
            self.vbox1.set_child_packing(self.sw2, False, *par2[1:])

    def update_bookmark(self):
        """ Update the book mark field """
        bookmark = str(self.ppr.get_bookmark() + 1)\
            if self.ppr.get_bookmark() is not None else 'N/A'
        self.get_object('lab_current_bookmark').set_text(bookmark)

    def update_status_line(self, position=None, total=None, percentage=None,
                           comments=None):
        if position is not None:
            self.labels['lab_current_pos'].set_text(str(position))
        if total is not None:
            self.labels['lab_total'].set_text(str(total))
        if percentage is not None:
            self.labels['lab_percentage'].set_text(str(percentage))
        if comments is not None:
            self.labels['lab_comments'].set_text(str(comments))

    def set_sensitive_nav_buttons(self, btn_status):
        self.get_object('btn_first').set_sensitive(btn_status[0])
        self.get_object('btn_previous').set_sensitive(btn_status[1])
        self.get_object('btn_next').set_sensitive(btn_status[2])
        self.get_object('btn_last').set_sensitive(btn_status[3])

    def check_for_new_comment_and_save_it(self):
        """ Check if the comment text buffer has been modified and if it has
        update the comment with the new content. The return value indicates
        whether the file has been saved.
        """
        if self.tb_comment.get_modified():
            self.ppr.update_comment(self.read_comment())
            self.ppr.save()
            self.tb_comment.set_modified(False)
            return True
        return False

    def open_file(self, filename):
        if self.ppr.active:
            self.ppr.save()
            # close ???
        
        # This call loads the file and sets active state,
        # it may generate exceptions
        try:
            actual_file, warnings = self.ppr.open(filename)
            self.get_object('poproofread').set_title(
                'PoProofRead - %s' % os.path.basename(actual_file))
            
            self.get_object('hbox_buttons').set_sensitive(True)
            self.get_object('hbox_statusline').set_sensitive(True)
            self.update_gui()

            for warning in warnings:
                WarningDialogOK(warning.title, warning.msg).run()

        except FileError as error:
            ErrorDialogOK(error.title, error.msg).run()

            
    def get_textbuffer_with_selection(self):
        if self.tb_diff.get_has_selection():
            return self.tb_diff
        elif self.tb_comment.get_has_selection():
            return self.tb_comment
        else:
            return None


def main():
    # Parse command line arguments for a file name to open
    description = 'Proofread po and podiff files.'
    usage = 'usage: %prog [options] filename'
    file_option_str = 'Path to one file that should be opened'
    n_arguments_str = ('incorrect number of arguments: {0}. 0 or 1 filenames '
                       'allowed.')
    version_str = '%prog {0}'.format(__init__.__version__)
    filename = None

    # Use argparse if available else optparse
    # REMOVE WHEN PYTHON 2.6 IS NO LONGER IN SERIOUS USE
    if 'argparse' in globals():
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('filename', default=None, nargs='?',
                            help=file_option_str)
        parser.add_argument('--version', action='version',
                            version=__init__.__version__)
        args = parser.parse_args()
        filename = args.filename

    else:
        parser = optparse.OptionParser(usage=usage,
                                       description=description,
                                       version=version_str)
        args = parser.parse_args()[1]  # parse_args gives (options, args)
        if len(args) == 1:
            filename = args[0]
        elif len(args) > 1:
            parser.error(n_arguments_str.format(len(args)))

    # Initiate program
    poproofread = PoProofReadGtkGUI()
    poproofread.get_object("poproofread").show()
    if filename is not None:
        poproofread.open_file(filename)
    gtk.main()

if __name__ == "__main__":
    main()
