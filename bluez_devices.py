from gi.repository import GLib
import dbus
import dbus.mainloop.glib


BLUEZ_BUS = "org.bluez"
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DEVICE_INTERFACE = "org.bluez.Device1"

SPP_UUID = "00001101-0000-1000-8000-00805f9b34fb"


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
system_bus = dbus.SystemBus()

def device_found(object_path):
    print(f"{object_path} found")
    # device = dbus.Interface(system_bus.get_object(BLUEZ_BUS, object_path), DEVICE_INTERFACE)
    # device.ConnectProfile(SPP_UUID)

def device_connected(object_path):
    print(f"{object_path} connected")

def device_disconnected(object_path):
    print(f"{object_path} disconnected")


object_manager = dbus.Interface(system_bus.get_object(BLUEZ_BUS, "/"), OBJECT_MANAGER_INTERFACE)

objects = object_manager.GetManagedObjects()
for object_path, interfaces in objects.items():
    if DEVICE_INTERFACE in interfaces:
        device_properties = interfaces[DEVICE_INTERFACE]
        if device_properties["Connected"] and SPP_UUID in device_properties["UUIDs"]:
            device_found(object_path)


# def interfaces_added(object_path, interfaces):
# 	if DEVICE_INTERFACE in interfaces:
# 		device_properties = interfaces[DEVICE_INTERFACE]
# 		if device_properties["Connected"] and SPP_UUID in device_properties["UUIDs"]:
# 			device_found(object_path)
#
# def interfaces_removed(object_path, interfaces_removed):
# 	pass
#
# system_bus.add_signal_receiver(interfaces_added, "InterfacesAdded", OBJECT_MANAGER_INTERFACE, BLUEZ_BUS)
# system_bus.add_signal_receiver(interfaces_removed, "InterfacesRemoved", OBJECT_MANAGER_INTERFACE, BLUEZ_BUS)


def properties_changed(interface, properties, removed_properties, object_path):
    if interface == DEVICE_INTERFACE:
        if "Connected" in properties:
            device = dbus.Interface(system_bus.get_object(BLUEZ_BUS, object_path), PROPERTIES_INTERFACE)
            uuids = device.Get(DEVICE_INTERFACE, "UUIDs")
            if SPP_UUID in uuids:
                if properties["Connected"]:
                    device_connected(object_path)
                else:
                    device_disconnected(object_path)

system_bus.add_signal_receiver(properties_changed, "PropertiesChanged", PROPERTIES_INTERFACE, BLUEZ_BUS, path_keyword="object_path")

GLib.MainLoop().run()