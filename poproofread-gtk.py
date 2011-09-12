# -*- coding: utf-8 -*-

"""
This file is a part of
poproofread -- A po-file and podiff proofreader
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

import os
import sys
import gtk
import pango
import argparse
from core import PoProofRead
	
class PoProofReadGtkGUI:

    def __init__(self):
        # Initiate core
        self.ppr = PoProofRead()

        self.builder = gtk.Builder()
        self.builder.add_from_file("poproofread-gtk-gui.glade") 
        
        self.window = self.builder.get_object("poproofread")
        self.builder.connect_signals(self)

        self.filech = self.builder.get_object("filechooserdialog_open")

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
        pangofont = pango.FontDescription('Monospace 10')
        self.builder.get_object('textview_diff').modify_font(pangofont)
        self.builder.get_object('textview_comment').modify_font(pangofont)

        self.reset_gui()

    # Mandatory gtk windown handling
    def on_window_destroy(self, widget):
        self.on_mnu_quit(widget)

    # GUI widgets
    def on_btn_set_bookmark(self, widget):
        self.ppr.set_bookmark()
        self.update_bookmark()
    
    def on_btn_jump_to_bookmark(self, widget):
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=self.ppr.get_bookmark())
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
        self.builder.get_object('dialog_jump_to').show()
        self.builder.get_object('spinbtn_jump_to')\
            .set_range(1, self.ppr.get_no_chunks())

    def on_mnu_open(self, widget):
        self.filech.show()

    def on_mnu_save(self, widget):
        if not self.check_for_new_comment_and_save_it():
            self.ppr.save()

    def on_mnu_quit(self, widget):
        if self.ppr.active:
            self.ppr.save()
        gtk.main_quit()

    def on_mnu_about(self, widget):
        pass

    def on_filech_ok(self, widget):
        if self.ppr.active:
            self.ppr.save()
        file = self.filech.get_filename()
        self.ppr.open(file)
        self.filech.hide()
        self.get_object('hbox_buttons').set_sensitive(True)
        self.get_object('hbox_statusline').set_sensitive(True)
        self.update_gui()

    def on_filech_cancel(self, widget):
        self.filech.hide()

    def on_jump_to_ok(self, widget):
        value = self.builder.get_object('spinbtn_jump_to').get_value_as_int()
        self.builder.get_object('dialog_jump_to').hide()
        self.check_for_new_comment_and_save_it()
        self.ppr.move(goto=value-1)
        self.update_gui()

    def on_jump_to_cancel(self, widget):
        self.builder.get_object('dialog_jump_to').hide()


    # General functions
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

    def reset_gui(self):
        welcome = 'Welcome to poproofread'
        self.write_to_textbuffer(self.tb_diff, welcome)
        for label in self.labels.values():
            label.set_text('-')
        self.get_object('hbox_buttons').set_sensitive(False)
        self.get_object('hbox_statusline').set_sensitive(False)

    def update_gui(self):
        if not self.ppr.active:
            return

        # Update text content
        content = self.ppr.get_current_content()
        self.write_to_textbuffer(self.tb_diff, content['diff_chunk'])
        self.write_to_textbuffer(self.tb_comment, content['comment'])
        startiter, enditer = self.tb_comment.get_bounds()
        self.builder.get_object('textview_comment').grab_focus()
        self.tb_comment.place_cursor(enditer)
        mark = self.tb_comment.create_mark(None, enditer)
        self.builder.get_object('textview_comment').scroll_mark_onscreen(mark)

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
        self.builder.get_object('lab_current_bookmark').set_text(bookmark)

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

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
                                     'Proofread po and podiff files.')
    parser.add_argument('filename', default=None, nargs='?',
                        help='The file to open')
    args = parser.parse_args()

    poproofread = PoProofReadGtkGUI()
    if args.filename is not None:
        poproofread.open_file_from_commandline(args.filename)
    poproofread.window.show()
    gtk.main()
