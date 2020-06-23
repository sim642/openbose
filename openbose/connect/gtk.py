from gi.repository import Gtk


class TextMenuItem(Gtk.MenuItem):
    def __init__(self, label: str):
        super().__init__()
        self.set_sensitive(False)
        self.set_label(label)