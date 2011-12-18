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

import os, sys, argparse
import pygtk
pygtk.require('2.0')
import pango, gtk, glib
from core import PoProofRead
from settings import Settings
import __init__
	
class PoProofReadGtkGUI:

    def __init__(self):
        # Get settings
        self.settings = Settings()

        # Initiate core
        self.ppr = PoProofRead()

        # Load gui and connect signals
        self.builder = gtk.Builder()
        moduledir=os.path.dirname(__file__)
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
            'lab_current_pos' : self.builder.get_object("lab_current_pos"),
            'lab_total' : self.builder.get_object("lab_total"),
            'lab_percentage' : self.builder.get_object("lab_percentage"),
            'lab_comments' : self.builder.get_object("lab_comments"),
            }

        # tb short for textbuffer
        self.tb_diff, self.tb_comment = gtk.TextBuffer(), gtk.TextBuffer()
        self.builder.get_object('textview_diff').set_buffer(self.tb_diff)   
        self.builder.get_object('textview_comment').set_buffer(self.tb_comment)
        self.clipboard = gtk.Clipboard()

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
        inline = widget.get_active()
        self.ppr.set_inline_status(inline)
        # If activating inline and empty comment, copy diff to comment field
        if inline and (self.read_comment() == '') and\
                (self.ppr.get_current_content()['comment'] == ''):
            self.ppr.update_comment(\
                self.ppr.get_current_content()['diff_chunk'])
            self.update_gui()

        # Update according to inline status
        par2 = self.vbox1.query_child_packing(self.sw2)
        if inline:
            self.vbox1.remove(self.sep1)
            self.vbox1.remove(self.sw1)
            self.sw2.set_size_request(-1, -1)
            self.vbox1.set_child_packing(self.sw2, True,  *par2[1:])
            #self.get_object('textview_diff').set_sensitive(False)
        else:
            self.vbox1.pack_start(self.sw1, True, True, 0)
            self.vbox1.reorder_child(self.sw1, 2)
            self.vbox1.pack_start(self.sep1, False, True, 0)
            self.vbox1.reorder_child(self.sep1, 3)
            self.sw2.set_size_request(-1, 100)            
            self.vbox1.set_child_packing(self.sw2, False, *par2[1:])
            #self.get_object('textview_diff').set_sensitive(True)

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

    def on_jump_to_ok(self, widget):
        value = self.get_object('spinbtn_jump_to').get_value_as_int()
        self.get_object('dialog_jump_to').hide()
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=value-1)
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
            if self.ppr.active:
                self.ppr.save()            

            actual_file = self.ppr.open(filename)
            self.get_object('poproofread').set_title(
                'PoProofRead - %s' % os.path.basename(actual_file))
            
            self.get_object('hbox_buttons').set_sensitive(True)
            self.get_object('hbox_statusline').set_sensitive(True)
            self.update_gui()
            self.settings['current_dir'] = self.filech.get_current_folder()
            self.filech.destroy()

    def on_filechooser_cancel(self, widget):
        self.filech.destroy()

    def on_mnu_save(self, widget):
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
            tb_with_selection.cut_clipboard(self.clipboard, True)

    def on_mnu_delete(self, widget):
        if not self.ppr.active:
            return
        if self.get_textbuffer_with_selection() is self.tb_comment:
            self.tb_comment.delete_selection(True, True)

    # Help menu
    def on_mnu_about(self, widget):
        # Reinitialize the dialog in case it has been destroyed
        self.builder.add_objects_from_file(self.gladefile,
                                           ['aboutdialog'])
        # Set version
        self.get_object('aboutdialog').set_version(__init__.__version__)
        # -4 and -6 equals destroy window and close button
        if self.get_object('aboutdialog').run() in [-4,-6]:
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

    def update_gui(self):
        if not self.ppr.active:
            return

        self.get_object('checkbutton_inline').set_active(
            self.ppr.get_inline_status())

        # Update text content
        content = self.ppr.get_current_content()
        self.write_to_textbuffer(self.tb_diff, content['diff_chunk'])
        self.write_to_textbuffer(self.tb_comment, content['comment'])
        # Move cursor to end of comment
        startiter, enditer = self.tb_comment.get_bounds()
        self.get_object('textview_comment').grab_focus()
        self.tb_comment.place_cursor(enditer)
        mark = self.tb_comment.create_mark(None, enditer)
        self.get_object('textview_comment').scroll_mark_onscreen(mark)

        # Get status and update sensitivity of buttons and the statusline
        status = self.ppr.get_status()
        self.update_status_line(str(status['current']+1), str(status['total']),
                                '%.0f%%' % status['percentage'],
                                str(status['comments']))
        if status['current'] == 0:
            self.set_sensitive_nav_buttons([False, False, True, True])
        elif status['current'] == status['total']-1:
            self.set_sensitive_nav_buttons([True, True, False, False])
        else:
            self.set_sensitive_nav_buttons([True, True, True, True])

        self.tb_comment.set_modified(False)

        self.update_bookmark()

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

    def open_file_from_commandline(self, filename):
        if self.ppr.active:
            self.ppr.save()
        self.ppr.open(filename)
        self.get_object('hbox_buttons').set_sensitive(True)
        self.get_object('hbox_statusline').set_sensitive(True)
        self.update_gui()

    def get_textbuffer_with_selection(self):
        if self.tb_diff.get_has_selection():
            return self.tb_diff
        elif self.tb_comment.get_has_selection():
            return self.tb_comment
        else:
            return None

def main():
    # Parse command line arguments for a file name to open
    parser = argparse.ArgumentParser(description=
                                     'Proofread po and podiff files.')
    parser.add_argument('filename', default=None, nargs='?',
                        help='The file to open')
    args = parser.parse_args()

    # Initiate program
    poproofread = PoProofReadGtkGUI()
    if args.filename is not None:
        poproofread.open_file_from_commandline(args.filename)
    poproofread.get_object("poproofread").show()
    gtk.main()

if __name__ == "__main__":
    main()
