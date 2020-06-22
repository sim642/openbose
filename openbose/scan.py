import gi

from gi.repository import GLib

import dbus
import dbus.mainloop.glib


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
system_bus = dbus.SystemBus()


BLUEZ_BUS = "org.bluez"
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DEVICE_INTERFACE = "org.bluez.Device1"
ADAPTER_INTERFACE = "org.bluez.Adapter1"


def properties_changed(interface, properties, removed_properties, object_path):
    if interface == DEVICE_INTERFACE:
        print(object_path, properties.get("ManufacturerData"))


def interfaces_added(object_path, interfaces):
    if DEVICE_INTERFACE in interfaces:
        device_properties = interfaces[DEVICE_INTERFACE]
        print(object_path, device_properties.get("ManufacturerData"))


def property_changed(name, value):
    if name == "Discovering" and not value:
        main_loop.quit()


system_bus.add_signal_receiver(properties_changed, "PropertiesChanged", PROPERTIES_INTERFACE, BLUEZ_BUS, arg0=DEVICE_INTERFACE, path_keyword="object_path")
system_bus.add_signal_receiver(interfaces_added, "InterfacesAdded", OBJECT_MANAGER_INTERFACE, BLUEZ_BUS)

system_bus.add_signal_receiver(property_changed, "PropertyChanged", ADAPTER_INTERFACE)

adapter = dbus.Interface(system_bus.get_object(BLUEZ_BUS, "/org/bluez/hci0"), ADAPTER_INTERFACE)
adapter.StartDiscovery()

main_loop = GLib.MainLoop()
main_loop.run()