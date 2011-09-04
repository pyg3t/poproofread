# -*- coding: utf-8 -*-
import sys
import gtk
import pango
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
        pangofont = pango.FontDescription('Monospace 12')
        self.builder.get_object('textview_diff').modify_font(pangofont)
        self.builder.get_object('textview_comment').modify_font(pangofont)

        self.reset_gui()

    # Mandatory gtk windown handling
    def on_window_destroy(self, widget):
        self.on_mnu_quit(widget)

    # GUI widgets
    def on_btn_set_bookmark(self, widget):
        print widget.get_property("label")
        print self.read_comment()
    
    def on_btn_jump_to_bookmark(self, widget):
        print widget.get_property("label")

    def on_btn_first(self, widget):
        print 'first'
        self.ppr.move(goto=0)
        self.update_gui()
    
    def on_btn_previous(self, widget):
        self.ppr.move(amount=-1)
        self.update_gui()

    def on_btn_next(self, widget):
        self.ppr.move(amount=1)
        self.update_gui()

    def on_btn_last(self, widget):
        self.ppr.move(goto=-1)
        self.update_gui()

    def on_btn_jump_to(self, widget):
        print "jump to"

    def on_mnu_open(self, widget):
        self.filech.show()

    def on_mnu_save(self, widget):
        print "save"

    def on_mnu_quit(self, widget):
        # Quit code
        gtk.main_quit()

    def on_mnu_about(self, widget):
        print "about"

    def on_filech_ok(self, widget):
        file = self.filech.get_filename()
        self.ppr.open(file)
        self.filech.hide()
        self.get_object('hbox_buttons').set_sensitive(True)
        self.get_object('hbox_statusline').set_sensitive(True)
        self.update_gui()

    def on_filech_cancel(self, widget):
        self.filech.hide()

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

        content = self.ppr.get_current_content()
        self.write_to_textbuffer(self.tb_diff, content['diff_chunk'])
        self.write_to_textbuffer(self.tb_comment, content['comment'])

        status = self.ppr.get_status()
        if status['current'] == 0:
            self.set_sensitive_nav_buttons([False, False, True, True])
        elif status['current'] == status['total']:
            self.set_sensitive_nav_buttons([True, True, False, False])
        else:
            self.set_sensitive_nav_buttons([True, True, True, True])
            
    def set_sensitive_nav_buttons(self, btn_status):
        self.get_object('btn_first').set_sensitive(btn_status[0])
        self.get_object('btn_previous').set_sensitive(btn_status[1])
        self.get_object('btn_next').set_sensitive(btn_status[2])
        self.get_object('btn_last').set_sensitive(btn_status[3])
        

            
    # Use tb.get_modified and tb.set_modified()
    
if __name__ == "__main__":
    poproofread = PoProofReadGtkGUI()
    poproofread.window.show()
    gtk.main()
