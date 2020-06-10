import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3

from gi.repository import GLib
gi.require_version("Notify", "0.7")
from gi.repository import Notify

import os.path
import signal
import threading


from bose import *

APPINDICATOR_ID = "openbose-tray"
NOTIFY_ID = "openbose-tray"

Notify.init(NOTIFY_ID)

indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, "audio-headphones", AppIndicator3.IndicatorCategory.HARDWARE)
# indicator.set_title("openbose")
indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

menu = Gtk.Menu()
item_name = Gtk.MenuItem(label="?")
item_name.set_sensitive(False)
menu.append(item_name)
item_battery = Gtk.MenuItem(label="Battery level: ?")
item_battery.set_sensitive(False)
menu.append(item_battery)
item_volume = Gtk.MenuItem(label="Volume: ?")
item_volume.set_sensitive(False)
menu.append(item_volume)
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
            write(Packet(FunctionBlock.SETTINGS, SettingsFunction.PRODUCT_NAME, Operator.GET))
            write(Packet(FunctionBlock.STATUS, StatusFunction.BATTERY_LEVEL, Operator.GET))
            write(Packet(FunctionBlock.AUDIO_MANAGEMENT, AudioManagementFunction.VOLUME, Operator.GET))

            while True:
                packet = read()
                GLib.idle_add(self.read_callback, packet)


notification_volume = Notify.Notification.new("Volume", None, "audio-headphones")
notification_volume.set_category("device")
notification_volume.set_hint("synchronous", GLib.Variant.new_string("volume")) # is this necessary?
notification_battery_level = Notify.Notification.new("Battery level", None, "audio-headphones")
notification_battery_level.set_category("device")


def read_callback(packet):
    if packet.function_block == FunctionBlock.SETTINGS and packet.function == SettingsFunction.PRODUCT_NAME and packet.operator == Operator.STATUS:
        name = packet.payload[1:]
        s = name.decode("utf-8")
        print(s)
        item_name.set_label(s)
    elif packet.function_block == FunctionBlock.STATUS and packet.function == StatusFunction.BATTERY_LEVEL and packet.operator == Operator.STATUS:
        battery_level = packet.payload[0]
        s = f"Battery level: {str(battery_level)}%"
        print(s)
        item_battery.set_label(s)

        notification_battery_level.set_property("body", f"{battery_level}%") # no set_body?
        notification_battery_level.show()
    elif packet.function_block == FunctionBlock.AUDIO_MANAGEMENT and packet.function == AudioManagementFunction.VOLUME and packet.operator == Operator.STATUS:
        max_volume = packet.payload[0]
        cur_volume = packet.payload[1]
        volume_percent = round(cur_volume / max_volume * 100)
        s = f"Volume: {volume_percent}% ({str(cur_volume)}/{str(max_volume)})"
        print(s)
        item_volume.set_label(s)

        notification_volume.set_hint("value", GLib.Variant.new_int32(volume_percent))
        notification_volume.show()


bose_thread = BoseThread("4C:87:5D:53:F2:CF", 8, read_callback)
bose_thread.setDaemon(True)

# signal.signal(signal.SIGINT, signal.SIG_DFL)
bose_thread.start()
Gtk.main()
