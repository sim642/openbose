import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3

from gi.repository import GLib


APPINDICATOR_ID = "indicator-recreate"


def step1():
    print("step1")
    global indicator1
    indicator1 = AppIndicator3.Indicator.new(APPINDICATOR_ID, "audio-headphones", AppIndicator3.IndicatorCategory.HARDWARE)
    indicator1.set_title("indicator1")
    indicator1.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    menu1 = Gtk.Menu()
    item1 = Gtk.MenuItem(label="item1")
    menu1.append(item1)
    menu1.show_all()
    indicator1.set_menu(menu1)


def step2():
    print("step2")
    global indicator1
    del indicator1
    # GLib.idle_add(step3)
    GLib.timeout_add(1000, step3)


def step3():
    print("step3")
    global indicator2
    indicator2 = AppIndicator3.Indicator.new(APPINDICATOR_ID, "audio-headphones",
                                             AppIndicator3.IndicatorCategory.HARDWARE)
    indicator2.set_title("indicator2")
    indicator2.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    menu2 = Gtk.Menu()
    item2 = Gtk.MenuItem(label="item2")
    menu2.append(item2)
    menu2.show_all()
    indicator2.set_menu(menu2)


step1()
# GLib.idle_add(step2)
GLib.timeout_add(1000, step2)


Gtk.main()