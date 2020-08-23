import collections
from typing import Optional, List

import gi

from openbose.connect.gtk import TextMenuItem, TextIconMenuItem
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

import yaml


from openbose import *

APPINDICATOR_ID = "openbose-tray" # TODO: make unique
NOTIFY_ID = "openbose-tray"

Notify.init(NOTIFY_ID)


def quit():
    Notify.uninit()
    Gtk.main_quit()


class PacketHandler:
    def on_packet(self, packet: Packet):
        pass


class BoseThread(threading.Thread):
    def __init__(self, address, channel, packet_handler: PacketHandler):
        super().__init__()
        self.address = address
        self.channel = channel
        self.packet_handler = packet_handler
        
        self.logger = logging.LoggerAdapter(logging.getLogger("BoseThread"), {"mac_address": address})

    def run(self) -> None:
        with Connection(self.address, self.channel) as conn:
            self.conn = conn

            self.write(productinfo.BmapVersionGetPacket())
            self.write(settings.ProductNameGetPacket())
            self.write(status.BatteryLevelGetPacket())
            self.write(audiomanagement.SourceGetPacket())
            self.write(audiomanagement.StatusGetPacket())
            self.write(audiomanagement.VolumeGetPacket())
            self.write(devicemanagement.ListDevicesGetPacket())
            self.write(audiomanagement.NowPlayingStartPacket())

            try:
                while True:
                    packet = self.read()
                    GLib.idle_add(self.packet_handler.on_packet, packet)
            except ConnectionResetError as e:
                # quit()
                self.logger.info("disconnected", exc_info=e)

    def write(self, packet: Packet):
        self.logger.debug("--> %s", packet)
        self.conn.write(packet)

    def read(self) -> Packet:
        packet = self.conn.read()
        self.logger.debug("<-- %s", packet)
        return packet


class PacketDispatcher(PacketHandler):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks = collections.defaultdict(list)

    def add(self, packet_type, callback):
        self.callbacks[packet_type].append(callback)

    def on_packet(self, packet: Packet):
        type_callbacks = self.callbacks[type(packet)]
        for callback in type_callbacks:
            callback(packet)


class Controller:
    bose_controller: "BoseController"

    def __init__(self, bose_controller: "BoseController") -> None:
        self.bose_controller = bose_controller

    @property
    def menu_items(self) -> List[Gtk.MenuItem]:
        return []


class VolumeController(Controller):
    item_volume: TextIconMenuItem
    notification_volume: GaugeNotification

    def __init__(self, bose_controller: "BoseController") -> None:
        super().__init__(bose_controller)

        self.item_volume = TextIconMenuItem(label="Volume: ?", icon_name="audio-volume-off")
        self.notification_volume = GaugeNotification("openbose", None, "audio-headphones")
        self.notification_volume.set_category("device")
        self.notification_volume.set_transient(True)

        self.bose_controller.packet_dispatcher.add(audiomanagement.VolumeStatusPacket, self.read_volume_status)

        self.logger = logging.LoggerAdapter(logging.getLogger("VolumeController"), {"mac_address": self.bose_controller.mac_address})  # TODO: centralize controller logger management

    @property
    def menu_items(self) -> List[Gtk.MenuItem]:
        return [self.item_volume]

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

        icon_name = None
        if volume_percent >= 2 / 3 * 100:
            icon_name = "audio-volume-high"
        elif volume_percent >= 1 / 3 * 100:
            icon_name = "audio-volume-medium"
        elif volume_percent > 0 / 3 * 100:
            icon_name = "audio-volume-low"
        else:
            icon_name = "audio-volume-muted"
        self.item_volume.set_icon(icon_name)


class BoseController:
    mac_address: str

    indicator: AppIndicator3.Indicator

    menu: Gtk.Menu
    item_name: TextMenuItem
    item_battery: TextIconMenuItem
    item_status_source: TextMenuItem
    item_title: TextMenuItem
    item_artist: TextMenuItem
    item_album: TextMenuItem

    notification_battery_level: MyNotification
    notification_connect: MyNotification
    notification_disconnect: MyNotification
    notification_source: MyNotification
    notification_status: MyNotification
    notification_now_playing: MyNotification

    bose_thread: BoseThread

    packet_dispatcher: PacketDispatcher
    volume_controller: VolumeController

    device_names: Dict[str, Optional[str]]
    source_mac_address: Optional[str]

    now_playing: Dict[audiomanagement.NowPlayingAttribute, str]

    INDICATORS: Dict[str, AppIndicator3.Indicator] = {}

    @classmethod
    def get_indicator(cls, mac_address: str) -> AppIndicator3.Indicator:
        if mac_address in cls.INDICATORS:
            return cls.INDICATORS[mac_address]
        else:
            indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID + "_" + mac_address, "audio-headphones",
                                                    AppIndicator3.IndicatorCategory.HARDWARE)
            cls.INDICATORS[mac_address] = indicator
            return indicator

    def __init__(self, mac_address: str):
        self.mac_address = mac_address

        self.packet_dispatcher = PacketDispatcher()

        self.indicator = self.get_indicator(mac_address)
        self.indicator.set_title("openbose")
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        self.item_name = TextMenuItem(label="?")
        self.menu.append(self.item_name)
        self.item_battery = TextIconMenuItem(label="Battery level: ?", icon_name="battery-missing")
        self.menu.append(self.item_battery)
        self.item_status_source = TextIconMenuItem(label="Source: ?", icon_name="gnome-unknown")  # TODO: don't use DE-specific icon?
        self.menu.append(self.item_status_source)

        def menu_append_all(items: List[Gtk.MenuItem]):
            for item in items:
                self.menu.append(item)

        self.volume_controller = VolumeController(self)
        menu_append_all(self.volume_controller.menu_items)

        self.menu.append(Gtk.SeparatorMenuItem())
        self.item_title = TextMenuItem(label="Title: ?")
        self.menu.append(self.item_title)
        self.item_artist = TextMenuItem(label="Artist: ?")
        self.menu.append(self.item_artist)
        self.item_album = TextMenuItem(label="Album: ?")
        self.menu.append(self.item_album)
        self.menu.append(Gtk.SeparatorMenuItem())
        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda _: quit())
        self.menu.append(item_quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.notification_battery_level = MyNotification("openbose", None, "audio-headphones")
        self.notification_battery_level.set_category("device")
        self.notification_connect = MyNotification("openbose", "Connected", "audio-headphones")
        self.notification_connect.set_category("device.added")
        self.notification_disconnect = MyNotification("openbose", "Disconnected", "audio-headphones")
        self.notification_disconnect.set_category("device.removed")
        self.notification_source = MyNotification("openbose", None, "audio-headphones")
        self.notification_source.set_category("device")
        self.notification_status = MyNotification("openbose", None, "audio-headphones")
        self.notification_status.set_category("device")
        self.notification_now_playing = MyNotification("openbose", None, "audio-headphones")
        self.notification_now_playing.set_category("device")

        self.packet_dispatcher.add(settings.ProductNameStatusPacket, self.read_product_name_status)
        self.packet_dispatcher.add(status.BatteryLevelStatusPacket, self.read_battery_level_status)
        self.packet_dispatcher.add(devicemanagement.DisconnectProcessingPacket, self.read_disconnect_processing)
        self.packet_dispatcher.add(devicemanagement.ListDevicesStatusPacket, self.read_devices_status)
        self.packet_dispatcher.add(devicemanagement.InfoStatusPacket, self.read_info_status)
        self.packet_dispatcher.add(audiomanagement.SourceStatusPacket, self.read_source_status)
        self.packet_dispatcher.add(audiomanagement.StatusStatusPacket, self.read_status_status)
        self.packet_dispatcher.add(audiomanagement.NowPlayingStatusPacket, self.read_now_playing_status)
        self.packet_dispatcher.add(audiomanagement.NowPlayingProcessingPacket, self.read_now_playing_processing)
        self.packet_dispatcher.add(audiomanagement.NowPlayingResultPacket, self.read_now_playing_result)

        self.logger = logging.LoggerAdapter(logging.getLogger("BoseController"), {"mac_address": mac_address})

        self.device_names = {}
        self.source_mac_address = None

        self.reset_now_playing()

    def read_product_name_status(self, packet: settings.ProductNameStatusPacket):
        name = packet.product_name
        s = name
        self.logger.info(s)
        self.indicator.set_title(s)
        self.item_name.set_label(s)
        self.volume_controller.notification_volume.set_summary(s)  # TODO: centralize controller name management
        self.notification_battery_level.set_summary(s)
        self.notification_connect.set_summary(s)
        self.notification_disconnect.set_summary(s)
        self.notification_source.set_summary(s)
        self.notification_status.set_summary(s)
        self.notification_now_playing.set_summary(s)

        self.notification_connect.show()

    def read_battery_level_status(self, packet: status.BatteryLevelStatusPacket):
        battery_level = packet.battery_level
        s = f"Battery level: {str(battery_level)}%"
        self.logger.info(s)
        self.item_battery.set_label(s)
        self.notification_battery_level.set_body(s)
        self.notification_battery_level.show()

        icon_name = None
        if battery_level >= 90:
            icon_name = "battery-100"
        elif battery_level >= 70:
            icon_name = "battery-080"
        elif battery_level >= 50:
            icon_name = "battery-060"
        elif battery_level >= 30:
            icon_name = "battery-040"
        elif battery_level >= 10:
            icon_name = "battery-020"
        else:
            icon_name = "battery-000"
        self.item_battery.set_icon(icon_name)

    def read_disconnect_processing(self, packet: devicemanagement.DisconnectProcessingPacket):
        self.notification_disconnect.show()
        self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

    def read_devices_status(self, packet: devicemanagement.ListDevicesStatusPacket):
        for mac_address in packet.mac_addresses:
            self.device_names[mac_address] = None
            self.bose_thread.write(devicemanagement.InfoGetPacket(mac_address))

    def read_info_status(self, packet: devicemanagement.InfoStatusPacket):
        self.device_names[packet.mac_address] = packet.name
        if packet.mac_address == self.source_mac_address:
            self.show_source()

    def read_source_status(self, packet: audiomanagement.SourceStatusPacket):
        self.source_mac_address = packet.mac_address
        self.show_source()
        # update audio status because different source may have different one (or not report any)
        self.bose_thread.write(audiomanagement.StatusGetPacket())
        self.bose_thread.write(audiomanagement.NowPlayingStartPacket())

    def show_source(self):
        mac_address = self.source_mac_address
        source = self.device_names.get(mac_address, mac_address)
        s = f"Source: {source}"
        self.logger.info(s)
        self.item_status_source.set_label(s)
        self.notification_source.set_body(s)
        self.notification_source.show()

    def read_status_status(self, packet: audiomanagement.StatusStatusPacket):
        icon_name = None
        status_name = None
        if packet.status == audiomanagement.Status.STOP:
            icon_name = "media-playback-stop"
            status_name = "stopped"
        elif packet.status == audiomanagement.Status.PLAY:
            icon_name = "media-playback-start"
            status_name = "playing"
        elif packet.status == audiomanagement.Status.PAUSE:
            icon_name = "media-playback-pause"
            status_name = "paused"
        else:
            icon_name = "gnome-unknown"  # TODO: don't use DE-specific icon?
            status_name = repr(packet.status)

        s = f"Status: {status_name}"
        self.logger.info(s)

        self.item_status_source.set_icon(icon_name)
        self.notification_status.set_body(s)
        self.notification_status.show()

    def read_now_playing_status(self, packet: audiomanagement.NowPlayingStatusPacket):
        s = f"Now playing: {packet.attribute!r}: {packet.value}"
        self.logger.info(s)

        if packet.attribute == audiomanagement.NowPlayingAttribute.SONG_TITLE:
            self.item_title.set_label(f"Title: {packet.value}")
            self.item_title.show()
        elif packet.attribute == audiomanagement.NowPlayingAttribute.ARTIST:
            self.item_artist.set_label(f"Artist: {packet.value}")
            self.item_artist.show()
        elif packet.attribute == audiomanagement.NowPlayingAttribute.ALBUM:
            self.item_album.set_label(f"Album: {packet.value}")
            self.item_album.show()

        self.now_playing[packet.attribute] = packet.value

    def reset_now_playing(self):
        self.now_playing = {}
        self.item_title.hide()
        self.item_artist.hide()
        self.item_album.hide()

    def read_now_playing_processing(self, packet: audiomanagement.NowPlayingProcessingPacket):
        self.reset_now_playing()

    def read_now_playing_result(self, packet: audiomanagement.NowPlayingProcessingPacket):
        ss = []
        if audiomanagement.NowPlayingAttribute.SONG_TITLE in self.now_playing:
            ss.append(f"Title: {self.now_playing[audiomanagement.NowPlayingAttribute.SONG_TITLE]}")
        if audiomanagement.NowPlayingAttribute.ARTIST in self.now_playing:
            ss.append(f"Artist: {self.now_playing[audiomanagement.NowPlayingAttribute.ARTIST]}")
        if audiomanagement.NowPlayingAttribute.ALBUM in self.now_playing:
            ss.append(f"Album: {self.now_playing[audiomanagement.NowPlayingAttribute.ALBUM]}")

        if ss:
            s = "\n".join(ss)
            self.logger.info(s)
            self.notification_now_playing.set_body(s)
            self.notification_now_playing.show()

    def connect(self):
        self.bose_thread = BoseThread(self.mac_address, 8, self.packet_dispatcher)
        self.bose_thread.setDaemon(True)
        self.bose_thread.start()


BLUEZ_BUS = "org.bluez"
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DEVICE_INTERFACE = "org.bluez.Device1"

SPP_UUID = "00001101-0000-1000-8000-00805f9b34fb"

with open("config.yml", "r", encoding="utf-8") as config_file:
    config = yaml.load(config_file)

bose_devices = config["devices"]

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
