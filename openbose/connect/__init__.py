import gi

from openbose.connect.gtk import TextMenuItem
from openbose.connect.notification import MyNotification, GaugeNotification

from openbose.packets import productinfo, settings, status, audiomanagement, devicemanagement

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3

from gi.repository import GLib
gi.require_version("Notify", "0.7")
from gi.repository import Notify

import dbus
import dbus.mainloop.glib

import threading

import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s %(mac_address)s %(message)s")


from openbose import *

APPINDICATOR_ID = "openbose-tray" # TODO: make unique
NOTIFY_ID = "openbose-tray"

Notify.init(NOTIFY_ID)


def quit():
    Notify.uninit()
    Gtk.main_quit()


class BoseThread(threading.Thread):
    def __init__(self, address, channel, read_callback):
        super().__init__()
        self.address = address
        self.channel = channel
        self.read_callback = read_callback
        
        self.logger = logging.LoggerAdapter(logging.getLogger("BoseThread"), {"mac_address": address})

    def run(self) -> None:
        with Connection(self.address, self.channel) as conn:

            def write(packet: Packet):
                self.logger.debug("--> %s", packet)
                conn.write(packet)

            def read() -> Packet:
                packet = conn.read()
                self.logger.debug("<-- %s", packet)
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
                # quit()
                self.logger.info("disconnected", exc_info=e)


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

    INDICATORS: Dict[str, AppIndicator3.Indicator] = {}

    @classmethod
    def get_indicator(cls, mac_address: str) -> AppIndicator3.Indicator:
        if mac_address in cls.INDICATORS:
            return cls.INDICATORS[mac_address]
        else:
            indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID + "/" + mac_address, "audio-headphones",
                                                    AppIndicator3.IndicatorCategory.HARDWARE)
            cls.INDICATORS[mac_address] = indicator
            return indicator

    def __init__(self, mac_address: str):
        self.mac_address = mac_address

        self.indicator = self.get_indicator(mac_address)
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

        self.logger = logging.LoggerAdapter(logging.getLogger("BoseController"), {"mac_address": mac_address})

    def read_product_name_status(self, packet: settings.ProductNameStatusPacket):
        name = packet.product_name
        s = name
        self.logger.info(s)
        self.item_name.set_label(s)
        self.notification_volume.set_summary(s)
        self.notification_battery_level.set_summary(s)
        self.notification_disconnect.set_summary(s)

    def read_battery_level_status(self, packet: status.BatteryLevelStatusPacket):
        battery_level = packet.battery_level
        s = f"Battery level: {str(battery_level)}%"
        self.logger.info(s)
        self.item_battery.set_label(s)
        self.notification_battery_level.set_body(s)
        self.notification_battery_level.show()

    def read_volume_status(self, packet: audiomanagement.VolumeStatusPacket):
        max_volume = packet.max_volume
        cur_volume = packet.cur_volume
        volume_percent = round(cur_volume / max_volume * 100)
        s = f"Volume: {volume_percent}% ({str(cur_volume)}/{str(max_volume)})"
        self.logger.info(s)
        self.item_volume.set_label(s)
        self.notification_volume.set_body(s)  # just in case if notifyd doesn't support value
        self.notification_volume.set_value(volume_percent)
        self.notification_volume.show()

    def read_disconnect_processing(self, packet: devicemanagement.DisconnectProcessingPacket):
        self.notification_disconnect.show()
        self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

    def read_unhandled(self, packet: Packet):
        pass

    def read_callback(self, packet: Packet):
        self.MAP.get(type(packet), self.read_unhandled)(packet)

    def connect(self):
        self.bose_thread = BoseThread(self.mac_address, 8, self.read_callback)
        self.bose_thread.setDaemon(True)
        self.bose_thread.start()


BLUEZ_BUS = "org.bluez"
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DEVICE_INTERFACE = "org.bluez.Device1"

SPP_UUID = "00001101-0000-1000-8000-00805f9b34fb"

bose_devices = {"4C:87:5D:53:F2:CF"}

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
system_bus = dbus.SystemBus()


class DeviceWatcher:

    def __init__(self):
        self.logger = logging.getLogger("DeviceWatcher")

    def start(self):
        self.find_current()

        system_bus.add_signal_receiver(self.properties_changed, "PropertiesChanged", PROPERTIES_INTERFACE, BLUEZ_BUS, path_keyword="object_path")
        # system_bus.add_signal_receiver(interfaces_added, "InterfacesAdded", OBJECT_MANAGER_INTERFACE, BLUEZ_BUS)
        # system_bus.add_signal_receiver(interfaces_removed, "InterfacesRemoved", OBJECT_MANAGER_INTERFACE, BLUEZ_BUS)

    def find_current(self):
        object_manager = dbus.Interface(system_bus.get_object(BLUEZ_BUS, "/"), OBJECT_MANAGER_INTERFACE)

        objects = object_manager.GetManagedObjects()
        for object_path, interfaces in objects.items():
            if DEVICE_INTERFACE in interfaces:
                device_properties = interfaces[DEVICE_INTERFACE]
                if device_properties["Connected"] and SPP_UUID in device_properties["UUIDs"]:
                    self.device_found(object_path)

    def properties_changed(self, interface, properties, removed_properties, object_path):
        if interface == DEVICE_INTERFACE:
            if "Connected" in properties:
                device = dbus.Interface(system_bus.get_object(BLUEZ_BUS, object_path), PROPERTIES_INTERFACE)
                uuids = device.Get(DEVICE_INTERFACE, "UUIDs")
                if SPP_UUID in uuids:
                    if properties["Connected"]:
                        self.device_connected(object_path)
                    else:
                        self.device_disconnected(object_path)

    # def interfaces_added(object_path, interfaces):
    # 	if DEVICE_INTERFACE in interfaces:
    # 		device_properties = interfaces[DEVICE_INTERFACE]
    # 		if device_properties["Connected"] and SPP_UUID in device_properties["UUIDs"]:
    # 			device_found(object_path)
    #
    # def interfaces_removed(object_path, interfaces_removed):
    # 	pass
    #

    def device_found(self, object_path):
        # print(f"{object_path} found")
        # device = dbus.Interface(system_bus.get_object(BLUEZ_BUS, object_path), DEVICE_INTERFACE)
        # device.ConnectProfile(SPP_UUID)
        self.device_connected(object_path)

    def device_connected(self, object_path):
        device = dbus.Interface(system_bus.get_object(BLUEZ_BUS, object_path), PROPERTIES_INTERFACE)
        mac_address = device.Get(DEVICE_INTERFACE, "Address")
        self.logger.info("connected", extra={"mac_address": mac_address})

        if mac_address in bose_devices:
            controller = BoseController(mac_address)
            controller.connect()

    def device_disconnected(self, object_path):
        device = dbus.Interface(system_bus.get_object(BLUEZ_BUS, object_path), PROPERTIES_INTERFACE)
        mac_address = device.Get(DEVICE_INTERFACE, "Address")
        self.logger.info("disconnected", extra={"mac_address": mac_address})


device_watcher = DeviceWatcher()
device_watcher.start()

# signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()