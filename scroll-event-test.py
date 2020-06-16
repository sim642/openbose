import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3


APPINDICATOR_ID = "scroll-event-test"

indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, "audio-headphones", AppIndicator3.IndicatorCategory.HARDWARE)
indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)


menu = Gtk.Menu()
item_quit = Gtk.MenuItem(label="Quit")
item_quit.connect("activate", lambda _: Gtk.main_quit())
menu.append(item_quit)
menu.show_all()
indicator.set_menu(menu)


def scroll_event(indicator, steps, direction):
    print(indicator, steps, direction)


indicator.connect("scroll-event", scroll_event)


Gtk.main()
