import sys
import gtk
	
class PoProofReadGtkGUI:

    def __init__(self):    
        builder = gtk.Builder()
        builder.add_from_file("poproofread-gtk-gui.glade") 
        
        self.window = builder.get_object("poproofread")
        builder.connect_signals(self)

        self.labels = {}
        self.labels['lab_current_pos'] = builder.get_object("lab_current_pos")
        self.labels['lab_total'] = builder.get_object("lab_total")
        self.labels['lab_percentage'] = builder.get_object("lab_percentage")
        self.labels['lab_comments'] = builder.get_object("lab_comment")

        # tv short for textview
        self.tv_diff = builder.get_object("textview_diff")
        self.tv_comment = builder.get_object("text_comment")

    # Mandatory gtk windown handling
    def on_window_destroy(self, widget, data=None):
        # Quit code
        gtk.main_quit()

    # GUI widgets
    def on_btn_set_bookmark(self, widget):
        print widget.get_property("label")
    
    def on_btn_jump_to_bookmark(self, widget):
        print widget.get_property("label")

    def on_btn_first(self, widget):
        print "first"
    
    def on_btn_previous(self, widget):
        print "previous"

    def on_btn_next(self, widget):
        print "next"

    def on_btn_last(self, widget):
        print "last"

    def on_btn_jump_to(self, widget):
        print "jump to"
    
if __name__ == "__main__":
    poproofread = PoProofReadGtkGUI()
    poproofread.window.show()
    gtk.main()
