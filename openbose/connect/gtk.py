from gi.repository import Gtk


class TextMenuItem(Gtk.MenuItem):
    def __init__(self, label: str):
        super().__init__()
        self.set_sensitive(False)
        self.set_label(label)


class IconMenuItem(Gtk.ImageMenuItem):
    def __init__(self, label: str, icon_name: str):
        super().__init__()
        self.set_label(label)
        self.set_icon(icon_name)

    def set_icon(self, icon_name):
        self.set_image(self.get_icon_image(icon_name))

    @staticmethod
    def get_icon_image(icon_name):
        return Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)


class TextIconMenuItem(IconMenuItem):
    def __init__(self, label: str, icon_name: str):
        super().__init__(label, icon_name)
        self.set_sensitive(False)
