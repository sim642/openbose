from gi.repository import GLib
import os
import fcntl
import dbus.service
import dbus.mainloop.glib

from openbose import *
import openbose.connection


class Profile(dbus.service.Object):
    fd = -1

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print("NewConnection(%s, %d)" % (path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

        # io_id = GLib.io_add_watch(self.fd, GLib.PRIORITY_DEFAULT, GLib.IO_IN | GLib.IO_PRI, self.io_cb)
        GLib.idle_add(self.do_stuff)

    def io_cb(self, fd, conditions):
        packet = os.read(fd, 4 + 255)
        print("<--", packet)
        return packet

    def do_stuff(self):
        os.set_blocking(self.fd, True)
        io = os.fdopen(self.fd, "r+b", buffering=0)
        print(io)
        conn = openbose.connection.ConnectionBase(io)
        print(conn)

        def write(packet: Packet):
            print("-->", packet)
            # os.write(self.fd, packet.to_bytes())
            conn.write(packet)

        def read() -> Packet:
            packet = conn.read()
            print("<--", packet)
            return packet

        write(Packet(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.BMAP_VERSION, Operator.GET))

        while read():
            pass

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))
        if self.fd > 0:
            os.close(self.fd)
            self.fd = -1


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
system_bus = dbus.SystemBus()
profile_manager = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")

profile_uuid = "00001101-0000-1000-8000-00805f9b34fb"
profile_path = "/foo/bar/profile"

profile = Profile(system_bus, profile_path)
mainloop = GLib.MainLoop()
opts = {
    "AutoConnect": True,
    "Name": "SPP Dev",
    "Role": "client",
    "Channel": dbus.UInt16(8),
    "ServiceRecord": """
        <?xml version="1.0" encoding="UTF-8" ?>
        <record>
          <attribute id="0x0001">
            <sequence>
              <uuid value="0x1101"/>
            </sequence>
          </attribute>
          <attribute id="0x0004">
            <sequence>
              <sequence>
                <uuid value="0x0100"/>
              </sequence>
              <sequence>
                <uuid value="0x0003"/>
                <uint8 value="8" name="channel"/>
              </sequence>
            </sequence>
          </attribute>
          <attribute id="0x0100">
            <text value="SPP Dev" name="name"/>
          </attribute>
        </record>
        """
}
# opts["RequireAuthoriation"] = True
# opts["RequireAuthentication"] = True

profile_manager.RegisterProfile(profile_path, profile_uuid, opts)
mainloop.run()