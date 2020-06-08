import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3

from gi.repository import GLib

import os.path
import signal
import threading


from bose import *

APPINDICATOR_ID = "openbose-tray"

indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, "audio-headphones", AppIndicator3.IndicatorCategory.HARDWARE)
# indicator.set_title("openbose")
indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

menu = Gtk.Menu()
item_battery = Gtk.MenuItem(label="")
item_battery.set_sensitive(False)
menu.append(item_battery)
menu.append(Gtk.SeparatorMenuItem())
item_quit = Gtk.MenuItem(label="Quit")
item_quit.connect("activate", lambda _: Gtk.main_quit())
menu.append(item_quit)
menu.show_all()
indicator.set_menu(menu)


class BoseThread(threading.Thread):
    def __init__(self, address, channel, read_callback):
        super().__init__()
        self.address = address
        self.channel = channel
        self.read_callback = read_callback

    def run(self) -> None:
        with Connection(self.address, self.channel) as conn:

            def write(packet: Packet):
                print("-->", packet)
                conn.write(packet)

            def read() -> Packet:
                packet = conn.read()
                print("<--", packet)
                return packet

            write(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.BMAP_VERSION, Operator.GET))
            write(Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET))

            while True:
                packet = read()
                GLib.idle_add(self.read_callback, packet)


def read_callback(packet):
    if packet.function == StatusFunction.BATTERY_LEVEL and packet.operator == Operator.STATUS:
        battery_level = packet.payload[0]
        s = "Battery level: " + str(battery_level)
        print(s)
        item_battery.set_label(s)


bose_thread = BoseThread("4C:87:5D:53:F2:CF", 8, read_callback)
bose_thread.setDaemon(True)

# signal.signal(signal.SIGINT, signal.SIG_DFL)
bose_thread.start()
Gtk.main()
