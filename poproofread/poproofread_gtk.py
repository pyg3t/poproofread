#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=W0613,W0142,R0904

"""
poproofread-gtk.py
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
import sys
import subprocess
try:
    import argparse
except ImportError:
    import optparse
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Pango
from gi.repository import Gtk
from gi.repository import Gdk
import glib
from core import PoProofRead
from settings import Settings
from custom_exceptions import FileError
from dialogs_gtk import ErrorDialogOK, WarningDialogOK, SaveAsDialog, \
    OpenDialog, AboutDialog, JumpToDialog, set_parent
from debug import level1, level2
import __init__
import i18n


class PoProofReadGtkGUI:
    """ The GTK frontend class for PoProofRead """

    def __init__(self, debug=0):
        # Set debug functions
        self.level = debug

        # Get settings
        self.settings = Settings()

        # Initiate core
        self.ppr = PoProofRead()

        # Load gui and connect signals
        #Was: self.builder = Gtk.Builder() experimental hack for i18n support
        self.builder = i18n.BUILDER
        moduledir = os.path.dirname(__file__)
        gladefile = os.path.join(moduledir,
                                      'gui/poproofread_gtk_gui.glade')
        iconfile = os.path.join(moduledir, 'graphics/192.png')

        try:
            self.builder.add_from_file(gladefile)
        except glib.GError as error:
            print "Your gtk version is not new enough:\n", error
            sys.exit(1)

        self.builder.connect_signals(self)
        self.gui('poproofread').set_icon_from_file(iconfile)
        set_parent(self.gui('poproofread'))

        self.clipboard = Gtk.Clipboard()

        # Color the background of the diff window grey
        self.gui('textview_diff').modify_base(
            self.gui('textview_diff').get_state(),
            Gdk.Color(red=58000, green=58000, blue=58000))

        # Used for move callback, arguments for self.ppr.move()
        self.moves = {self.gui('btn_first'):    {'goto': 0},
                      self.gui('btn_previous'): {'amount': -1},
                      self.gui('btn_next'):     {'amount': 1},
                      self.gui('btn_last'):     {'goto': -1}}

        self.settings_to_gui()
        self.reset_gui()

    # Mandatory gtk window handling
    @level1
    def on_window_destroy(self, widget):
        """ Callback for "window destroy" event """
        self.on_mnu_quit(widget)

    ### GUI widgets
    # Buttons
    @level1
    def on_btn_set_bookmark(self, widget):
        """ Callback for "set bookmark" button """
        self.ppr.set_bookmark()
        self.update_bookmark()

    @level1
    def on_btn_jump_to_bookmark(self, widget):
        """ Callback for "jump to bookmark" button """
        self.check_for_new_comment_and_save()
        self.ppr.move(goto=self.ppr.get_bookmark())
        self.update_gui()

    @level1
    def on_checkbutton_inline(self, widget):
        """ Callback for inline toggle button """
        self.check_for_new_comment_and_save()
        self.ppr.set_inline_status(widget.get_active())
        self.update_gui()

    @level2
    def on_move(self, widget):
        """ Callback for all navigation buttons """
        self.check_for_new_comment_and_save()
        # ** passes all key=values in self.moves[widget] as arguments
        self.ppr.move(**self.moves[widget])
        self.update_gui()

    @level1
    def on_btn_jump_to(self, widget):
        """ Callback for "jump to" button """
        value = JumpToDialog(1, self.ppr.get_no_chunks()).run()
        if value is not None:
            self.check_for_new_comment_and_save()
            self.ppr.move(goto=value - 1)
            self.update_gui()

    # Menus
    # File menu
    @level1
    def on_mnu_open(self, widget):
        """ Callback for "open" menu item """
        filename, current_dir = OpenDialog(self.settings['current_dir']).run()
        if filename is not None:
            self.settings['current_dir'] = current_dir
            self.open_file(filename)

    @level1
    def on_mnu_save(self, widget):
        """ Callback for "save" menu item. Insensitive if inactive """
        self.check_for_new_comment_and_save()

    @level1
    def on_mnu_save_as(self, widget):
        """ Callback for "save as" menu item. Insensitive if inactive """
        new_filename, current_dir = \
            SaveAsDialog(self.settings['current_dir']).run()
        if new_filename is not None:
            if current_dir is not None:
                self.settings['current_dir'] = current_dir
            ok_to_save, actual_filename = \
                self.ppr.set_new_save_location(new_filename)
            if ok_to_save:
                self.toggle_active_and_set_filename(True, actual_filename)
                self.check_for_new_comment_and_save()

    @level1
    def on_mnu_close(self, widget):
        """ Callback for "close" menu item """
        if self.ppr.active:
            self.check_for_new_comment_and_save()
            self.ppr.close()
            self.reset_gui()

    @level1
    def on_mnu_import_clipboard(self, widget):
        """ Import the contents of the clipboard """
        # The method below converts into utf-8 which means that character
        # code information is lost
        text = self.clipboard.wait_for_text()
        if text is not None:
            self.on_mnu_close(None)

            filename = self.ppr.import_from_text(text)
            self.toggle_active_and_set_filename(True, filename)
            self.update_gui()

    @level1
    def on_mnu_export_clipboard(self, widget):
        """ Callback for "Export to clipoard" menu item """
        text = self.ppr.save(clipboard=True)[1]
        self.clipboard.set_text(text)

    @level1
    def on_mnu_quit(self, widget):
        """ Callback for "quit" menu item """
        if self.ppr.active:
            self.check_for_new_comment_and_save()

        self.settings.write()
        Gtk.main_quit()

    ########################################
    # Edit menu
    @level1
    def on_mnu_copy(self, widget):
        """ Callback for "copy" menu item """
        tb_with_selection = self.get_textbuffer_with_selection()
        if tb_with_selection is not None:
            tb_with_selection.copy_clipboard(self.clipboard)

    @level1
    def on_mnu_paste(self, widget):
        """ Callback for "paste" menu item """
        self.gui('textbuffer_comment').\
            paste_clipboard(self.clipboard, None, True)

    @level1
    def on_mnu_cut(self, widget):
        """ Callback for "cut" menu item """
        if self.get_textbuffer_with_selection() is\
                self.gui('textbuffer_comment'):
            self.gui('textbuffer_comment').cut_clipboard(self.clipboard, True)

    @level1
    def on_mnu_delete(self, widget):
        """ Callback for "delete" menu item """
        if self.get_textbuffer_with_selection() is\
                self.gui('textbuffer_comment'):
            self.gui('textbuffer_comment').delete_selection(True, True)

    ########################################
    # Help menu
    def on_mnu_about(self, widget):  # pylint: disable=R0201
        """ Callback for "about" menu item """
        AboutDialog().run()

    def on_mnu_help_activate(self, widget):  # pylint: disable=R0201
        """ Callback for "help" menu item """
        process = subprocess.Popen('which yelp > /dev/null', shell=True)
        if process.wait() == 0:
            command = 'yelp {0} &'.format(
                os.path.join(os.path.dirname(__file__), 'doc', 'C')
                )
            subprocess.Popen(command, shell=True)
        else:
            warning = ('You need to have the program "yelp" installed to read '
                       'the documentation')
            WarningDialogOK('Missing program: "yelp"', warning).run()

    ### General functions ####################################################
    def gui(self, name):
        """ Convinience method to get gui widget """
        return self.builder.get_object(name)

    def write_to_textbuffer(self, textbuffer_name, text):
        """ Deletes anything in textbuffer and replaces it with text """
        startiter, enditer = self.gui(textbuffer_name).get_bounds()
        self.gui(textbuffer_name).delete(startiter, enditer)
        self.gui(textbuffer_name).insert(startiter, text)

    def read_comment(self):
        """ Return the content of the comment window """
        startiter, enditer = self.gui('textbuffer_comment').get_bounds()
        return self.gui('textbuffer_comment').get_text(startiter, enditer,
                                                       include_hidden_chars=False)

    def settings_to_gui(self):
        """ Update the gui according to the settings """
        pangofont = Pango.FontDescription(
            'Monospace {0}'.format(self.settings['font_size']))
        self.gui('textview_diff').modify_font(pangofont)
        self.gui('textview_comment').modify_font(pangofont)

    def reset_gui(self):
        """ Reset the gui to start up mode """
        welcome = _('Welcome to PoProofRead version {0}\n\n'
                    'To use PoProofRead simply load the podiff you wish to '
                    'proofread, move through the file with PageUp and PageDown'
                    ' and when you wish to make a comment, just start typing. '
                    'The program will auto-save everytime you move away from a'
                    ' new comment.\n\n'
                    'Keyboard shortcuts:\n'
                    'Previous part  : PageUp     Next part     : PageDown\n'
                    'First part     : Ctrl-Home  Last          : Ctrl-End\n'
                    '\n'
                    'Toggle inline commenting: Ctrl-i\n'
                    'Import from clipboard   : Ctrl-shift-i\n'
                    'Export to clipboard     : Ctrl-shift-e\n'
                    '\n'
                    'Set bookmark   : Ctrl-b     Go to bookmark: Ctrl-g\n'
                    'Jump to part # : Ctrl-j\n'
                    '\n'
                    'Open file      : Ctrl-o     Save file     : Ctrl-s\n'
                    'Close file     : Ctrl-w     Save file as  : '
                                                            'Ctrl-shift-s\n'
                    'Quit           : Ctrl-q\n'
                    '\n'
                    'Copy           : Ctrl-c     Cut           : Ctrl-x\n'
                    'Paste          : Ctrl-v     Delete        : Delete\n\n'
                    'If in doubt, just move the mouse over the button and the '
                    'keyboard shortcut will be in the tool tip.')\
                    .format(__init__.__version__)
        self.write_to_textbuffer('textbuffer_diff', welcome)
        self.write_to_textbuffer('textbuffer_comment', '')
        self.update_status_line()
        self.toggle_active_and_set_filename(False)
        self.update_inline_gui(False)
        self.gui('mnu_close').set_sensitive(False)

    def update_gui(self):
        """ update the gui from current poproofread state """
        if not self.ppr.active:
            self.gui('mnu_close').set_sensitive(False)
            return
        self.gui('mnu_close').set_sensitive(True)

        # Read inline status from ppr and update checkbutton accordingly
        inline = self.ppr.get_inline_status()
        self.gui('checkbutton_inline').handler_block_by_func(
            self.on_checkbutton_inline)
        self.gui('checkbutton_inline').set_active(inline)
        self.gui('checkbutton_inline').handler_unblock_by_func(
            self.on_checkbutton_inline)
        self.update_inline_gui(inline)

        # Update text content
        content = self.ppr.get_current_content()
        self.write_to_textbuffer('textbuffer_diff', content['diff_chunk'])
        self.write_to_textbuffer('textbuffer_comment', content['comment'])
        self.gui('textbuffer_comment').set_modified(False)
        # Move cursor to end of comment
        # get_bounds returns (startiter, enditer)
        enditer = self.gui('textbuffer_comment').get_bounds()[1]
        self.gui('textview_comment').grab_focus()
        self.gui('textbuffer_comment').place_cursor(enditer)
        mark = self.gui('textbuffer_comment').create_mark(None, enditer)
        self.gui('textview_comment').scroll_mark_onscreen(mark)

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

        self.update_bookmark()

    def update_inline_gui(self, inline):
        """ Update the gui to the current inline status
        sw is short for scrolled window, sw1 is for diff and sw2 is for comment
        hsep is the horizontal separator
        par2 are the last ([1:]) sw2 packaging parameters in vbox
        """
        par2 = self.gui('vbox').query_child_packing(self.gui('sw2'))[1:]
        if inline and self.gui('sw1') in self.gui('vbox'):
            # If inline and not already in inline layout ...
            self.gui('vbox').remove(self.gui('hsep'))
            self.gui('vbox').remove(self.gui('sw1'))
            self.gui('sw2').set_size_request(-1, -1)
            self.gui('vbox').set_child_packing(self.gui('sw2'), True, *par2)
        elif not (inline or self.gui('sw1') in self.gui('vbox')):
            # ... and vice versa
            self.gui('vbox').pack_start(self.gui('sw1'), True, True, 0)
            self.gui('vbox').reorder_child(self.gui('sw1'), 2)
            self.gui('vbox').pack_start(self.gui('hsep'), False, True, 0)
            self.gui('vbox').reorder_child(self.gui('hsep'), 3)
            self.gui('sw2').set_size_request(-1, 100)
            self.gui('vbox').set_child_packing(self.gui('sw2'), False, *par2)

    def update_bookmark(self):
        """ Update the book mark field """
        bookmark = str(self.ppr.get_bookmark() + 1)\
            if self.ppr.get_bookmark() is not None else 'N/A'
        self.gui('lab_current_bookmark').set_text(bookmark)

    def update_status_line(self, current_pos='-', total='-', percentage='-',
                           comments='-'):
        """ Update the statue line part of the gui. The '-' strings are used
        if no proofreading is loaded
        """
        for name in ['current_pos', 'total', 'percentage', 'comments']:
            self.gui('lab_{0}'.format(name)).set_text(locals()[name])

    def set_sensitive_nav_buttons(self, statuses):
        """ Sets the sensitivity of the navigation buttons in accordance with
        the position. statuses are ['first', 'previous', 'next', 'last']
        """
        for num, name in enumerate(['first', 'previous', 'next', 'last']):
            self.gui('btn_{0}'.format(name)).set_sensitive(statuses[num])

    def check_for_new_comment_and_save(self):
        """ Check if the comment text buffer has been modified and if it has
        update the comment with the new content. The return value indicates
        whether the file has been saved.
        """
        if self.gui('textbuffer_comment').get_modified():
            self.ppr.update_comment(self.read_comment())
            self.gui('textbuffer_comment').set_modified(False)
        warning = self.ppr.save()[0]
        if warning is not None:
            WarningDialogOK(warning.title, warning.msg).run()

    @level1
    def open_file(self, filename):
        """ Open file logic, factored out for use both from gui and cli """
        self.on_mnu_close(None)
        # This call loads the file and sets active state,
        # it may generate exceptions
        try:
            actual_file, warnings = self.ppr.open(filename)
            self.toggle_active_and_set_filename(True, actual_file)
            self.update_gui()
            for warning in warnings:
                WarningDialogOK(warning.title, warning.msg).run()

        except FileError as error:
            ErrorDialogOK(error.title, error.msg).run()

    def get_textbuffer_with_selection(self):
        """ Return the text buffer with an active text selection """
        if self.gui('textbuffer_diff').get_has_selection():
            return self.gui('textbuffer_diff')
        elif self.gui('textbuffer_comment').get_has_selection():
            return self.gui('textbuffer_comment')
        else:
            return None

    def toggle_active_and_set_filename(self, active, filename=None):
        """ Set filename in title and activate buttons and statusline """
        title = 'PoProofRead {0}'.format(__init__.__version__)
        if filename is not None:
            title = '{0} - PoProofRead'.format(filename)
        self.gui('poproofread').set_title(title)
        self.gui('hbox_buttons').set_sensitive(active)
        self.gui('hbox_statusline').set_sensitive(active)
        for button in ['save', 'save_as', 'export_clipboard', 'cut', 'copy',
                        'paste', 'delete']:
            self.gui('mnu_{0}'.format(button)).set_sensitive(active)


def main():
    """ Parse command line parameters and initiate gtk gui """
    # Parse command line arguments for a file name to open
    description = 'Proofread po and podiff files.'
    usage = 'usage: %prog [options] filename'
    file_option_str = 'Path to one file that should be opened'
    n_arguments_str = ('incorrect number of arguments: {0}. 0 or 1 filenames '
                       'allowed.')
    debug_str = 'debug level 0-2. Default 0 means debug off'
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
        parser.add_argument('--debug', default=0, type=int, help=debug_str)
        args = parser.parse_args()
        debug = args.debug
        filename = args.filename
    else:
        parser = optparse.OptionParser(usage=usage,
                                       description=description,
                                       version=version_str)
        parser.add_option('-d', '--debug', default=0, help=debug_str)
        options, args = parser.parse_args()  # parse_args gives (options, args)
        debug = options.debug
        if len(args) == 1:
            filename = args[0]
        elif len(args) > 1:
            parser.error(n_arguments_str.format(len(args)))

    # Initiate program
    poproofread = PoProofReadGtkGUI(debug)
    poproofread.gui("poproofread").show()
    if filename is not None:
        poproofread.open_file(filename)
    Gtk.main()

if __name__ == "__main__":
    main()
