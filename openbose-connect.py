import gi

from bose.packets import productinfo, settings, status, audiomanagement, devicemanagement

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

APPINDICATOR_ID = "openbose-tray" # TODO: make unique
NOTIFY_ID = "openbose-tray"

Notify.init(NOTIFY_ID)


def quit():
    Notify.uninit()
    Gtk.main_quit()


class TextMenuItem(Gtk.MenuItem):
    def __init__(self, label: str):
        super().__init__()
        self.set_sensitive(False)
        self.set_label(label)


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

            write(productinfo.BmapVersionGetPacket())
            write(settings.ProductNameGetPacket())
            write(status.BatteryLevelGetPacket())
            write(audiomanagement.VolumeGetPacket())

            try:
                while True:
                    packet = read()
                    GLib.idle_add(self.read_callback, packet)
            except ConnectionResetError as e:
                quit()


class MyNotification(Notify.Notification):
    def __init__(self, summary: str, body: str = None, icon: str = None):
        super().__init__()
        self.update(summary, body, icon)

    def set_summary(self, summary: str):
        self.set_property("summary", summary)

    def set_body(self, body: str = None):
        self.set_property("body", body)

    def set_transient(self, transient: bool):
        """Sets notification logging."""
        self.set_hint("transient", GLib.Variant.new_boolean(transient))


class GaugeNotification(MyNotification):
    def __init__(self, summary: str, body: str = None, icon: str = None):
        super().__init__(summary, body, icon)
        self.set_hint("synchronous", GLib.Variant.new_string("volume"))  # what does this value mean?
        self.set_hint("x-canonical-private-synchronous", GLib.Variant.new_string(""))

    def set_value(self, value: int):
        self.set_hint("value", GLib.Variant.new_int32(value))


class BoseController:
    mac_address: str

    indicator: AppIndicator3.Indicator

    menu: Gtk.Menu
    item_name: Gtk.MenuItem
    item_battery: Gtk.MenuItem
    item_volume: Gtk.MenuItem

    notification_volume: GaugeNotification
    notification_battery_level: MyNotification
    notification_disconnect: MyNotification

    bose_thread: BoseThread

    def __init__(self, mac_address: str):
        self.mac_address = mac_address

        self.indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, "audio-headphones",
                                                     AppIndicator3.IndicatorCategory.HARDWARE)
        # self.indicator.set_title("openbose")
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        self.item_name = TextMenuItem(label="?")
        self.menu.append(self.item_name)
        self.item_battery = TextMenuItem(label="Battery level: ?")
        self.menu.append(self.item_battery)
        self.item_volume = TextMenuItem(label="Volume: ?")
        self.menu.append(self.item_volume)
        self.menu.append(Gtk.SeparatorMenuItem())
        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda _: quit())
        self.menu.append(item_quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.notification_volume = GaugeNotification("openbose", None, "audio-headphones")
        self.notification_volume.set_category("device")
        self.notification_volume.set_transient(True)
        self.notification_battery_level = MyNotification("openbose", None, "audio-headphones")
        self.notification_battery_level.set_category("device")
        self.notification_disconnect = MyNotification("openbose", "Disconnected", "audio-headphones")
        self.notification_disconnect.set_category("device.removed")

        self.MAP = {
            settings.ProductNameStatusPacket: self.read_product_name_status,
            status.BatteryLevelStatusPacket: self.read_battery_level_status,
            audiomanagement.VolumeStatusPacket: self.read_volume_status,
            devicemanagement.DisconnectProcessingPacket: self.read_disconnect_processing,
        }

    def read_product_name_status(self, packet: settings.ProductNameStatusPacket):
        name = packet.product_name
        s = name
        print(s)
        self.item_name.set_label(s)
        self.notification_volume.set_summary(s)
        self.notification_battery_level.set_summary(s)
        self.notification_disconnect.set_summary(s)

    def read_battery_level_status(self, packet: status.BatteryLevelStatusPacket):
        battery_level = packet.battery_level
        s = f"Battery level: {str(battery_level)}%"
        print(s)
        self.item_battery.set_label(s)
        self.notification_battery_level.set_body(s)
        self.notification_battery_level.show()

    def read_volume_status(self, packet: audiomanagement.VolumeStatusPacket):
        max_volume = packet.max_volume
        cur_volume = packet.cur_volume
        volume_percent = round(cur_volume / max_volume * 100)
        s = f"Volume: {volume_percent}% ({str(cur_volume)}/{str(max_volume)})"
        print(s)
        self.item_volume.set_label(s)
        self.notification_volume.set_body(s)  # just in case if notifyd doesn't support value
        self.notification_volume.set_value(volume_percent)
        self.notification_volume.show()

    def read_disconnect_processing(self, packet: devicemanagement.DisconnectProcessingPacket):
        self.notification_disconnect.show()

    def read_unhandled(self, packet: Packet):
        pass

    def read_callback(self, packet: Packet):
        self.MAP.get(type(packet), self.read_unhandled)(packet)

    def connect(self):
        self.bose_thread = BoseThread(self.mac_address, 8, self.read_callback)
        self.bose_thread.setDaemon(True)
        self.bose_thread.start()


controller = BoseController("4C:87:5D:53:F2:CF")
controller.connect()

# signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
