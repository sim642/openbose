# Bose APIs
* [General Bose QC 35 II on linux user guide](https://flx.ai/2019/bose-qc35ii-linux)
* [StackOverflow with choices](https://stackoverflow.com/a/59709851/854540)
* BLE GATT: proprietary?
    * [Email exchange: GATT vs AT](https://www.spinics.net/lists/linux-bluetooth/msg74218.html)
* HFP/A2DP: AT commands `AT+XAPL` & `AT+IPHONEACCEV`
    * [Apple documentation](https://developer.apple.com/accessories/Accessory-Design-Guidelines.pdf)
    * [Bluetooth_Headset_Battery_Level](https://github.com/TheWeirdDev/Bluetooth_Headset_Battery_Level)
    * [Pulseaudio logging hack](https://github.com/sre/pulseaudio/commit/d66b66d20e9bc73e6d0ca89283cf2b5675304b00)
        * [Email exchange: Pulseaudio vs BlueZ](https://www.spinics.net/lists/linux-bluetooth/msg74218.html)
* SPP: reverse-engineered Bmap protocol
    * [based-connect (CLI tool)](https://github.com/Denton-L/based-connect)
        * [based.c (implemented commands)](https://github.com/Denton-L/based-connect/blob/master/based.c)
        * [details.txt (unimplemented commands)](https://github.com/Denton-L/based-connect/blob/master/details.txt)
    * [Bose_QC35_Android (Android app)](https://github.com/DavidVentura/Bose_QC35_Android)
        * [Protocol.kt](https://github.com/DavidVentura/Bose_QC35_Android/blob/master/app/src/main/java/com/bose/control/Protocol.kt)


# Linux APIs
## Power APIs
* [UPower](https://upower.freedesktop.org/)
    * [GitLab](https://gitlab.freedesktop.org/upower/upower)
    * [up-device-bluez.c](https://cgit.freedesktop.org/upower/tree/src/linux/up-device-bluez.c)
    * [UPowerGlib.Device](https://lazka.github.io/pgi-docs/#UPowerGlib-1.0/classes/Device.html)
* power_supply class
    * [power_supply_class.txt](https://www.kernel.org/doc/Documentation/power/power_supply_class.txt)
    * [Power Supply Subsystem slides](https://elinux.org/images/4/45/Power-supply_Sebastian-Reichel.pdf)
* HID battery level/strength
    * [hid.h](https://github.com/torvalds/linux/blob/a2f0b878c3ca531a1706cb2a8b079cea3b17bafc/include/linux/hid.h#L572)
    * [hid-input.c](https://github.com/torvalds/linux/blob/e69ec487b2c7c82ef99b4b15122f58a2a99289a3/drivers/hid/hid-input.c#L283)

# Communication APIs
* D-Bus
    * [D-Bus tutorial](https://dbus.freedesktop.org/doc/dbus-tutorial.html)
    * [Python example](https://stackoverflow.com/questions/21793826/simple-but-specific-listener-and-sender-python-3-dbus-example)
    * [Python tutorial](https://www.gkbrk.com/2018/02/simple-dbus-service-in-python/)
    * [dbus-python tutorial](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)
    * [org.mpris.Mediaplyer2 discovery by prefix](https://stackoverflow.com/a/20961735/854540)
* [Linux Bluetooth stack overview](https://opensourceforu.com/2015/06/linux-without-wires-the-basics-of-bluetooth/)
* BlueZ
    * D-Bus `org.bluez.Battery1`
        * [battery-api.txt](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/battery-api.txt)
        * [bluez/battery.c](https://github.com/hadess/bluez/blob/477ecca127c529611adbc53f08039cefaf86305d/profiles/battery/battery.c#L55)
    * D-Bus `org.bluez.ProfileManager1`
        * [BlueZ 5.0](https://lwn.net/Articles/531133/)
        * [profile-api.txt](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt)
        * [Profile registration in Python](https://stackoverflow.com/questions/52558519/bluez-profile-registration)
        * [Profile registration in C#?](https://blog.mrgibbs.io/bluetooth-profile-with-bluez-mono/)


# GUI (GTK)
* [PyGObject/gi.repository documentation](https://pygobject.readthedocs.io/en/latest/index.html)
* [Python GTK+ 3 tutorial](https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html)
* [GTK inspector](https://askubuntu.com/a/748152)
* Tray icon
    * AppIndicator
        * [Step-by-step Python guide](http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html)
        * [StatusNotifierItem over D-Bus](https://www.freedesktop.org/wiki/Specifications/StatusNotifierItem/)
    * Ayatana
        * AppIndicator predecessor?
    * StatusIcon (deprecated)
        * Syncthing (different StatusIcon implementations?)
            * [statusicon.py](https://github.com/kozec/syncthing-gtk/blob/master/syncthing_gtk/statusicon.py)
    * XAppStatusIcon (Linux Mint reimplementation)
        * [Linux Mint news blog](https://blog.linuxmint.com/?p=3795)
    * Solaar (AppIndicator/Ayatana/StatusIcon)
        * [tray.py](https://github.com/pwr-Solaar/Solaar/blob/master/lib/solaar/ui/tray.py)
* ScaleMenuItem
    * [Not supported in AppIndicator via dbusmenu](https://askubuntu.com/a/57276)
        * [libdbusmenu](https://launchpad.net/libdbusmenu)
            * [GitHub](https://github.com/AyatanaIndicators/libdbusmenu)
    * [xfce4-power-manager scalemenuitem.c](https://gitlab.xfce.org/xfce/xfce4-power-manager/-/blob/master/panel-plugins/power-manager-plugin/scalemenuitem.c)
        * [Python reimplementation](https://github.com/pmrv/brightnessicon/blob/396a1164f8edb829bfa0e93d84e5aabf97246974/brightnessicon#L70)
    * [AyatanaIdo3.ScaleMenuItem](https://lazka.github.io/pgi-docs/#AyatanaIdo3-0.4/classes/ScaleMenuItem.html)
        * [ayatana-ido/idoscalemenuitem.c](https://github.com/AyatanaIndicators/ayatana-ido/blob/master/src/idoscalemenuitem.c)
* Notifications
    * [Specification](https://developer.gnome.org/notification-spec/)
    * [Step-by-step Python guide](http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html)
    * Progress bar/gauge, `value` hint
        * [notify-send, `synchronous` hint](https://ubuntuforums.org/showthread.php?t=1776148)
        * [Python](https://stackoverflow.com/a/41890837/854540)
        * [Summary & body not shown in xfce4-notifyd](https://gitlab.xfce.org/apps/xfce4-notifyd/-/issues/4)
        * [xfce4-pulseaudio-plugin, `x-canonical-private-synchronous` hint](https://gitlab.xfce.org/panel-plugins/xfce4-pulseaudio-plugin/-/blob/fd1e12412eec41a5cd787321f90222fd07da976c/panel-plugin/pulseaudio-notify.c#L229-231)
    * No logging, `transient` hint
        * [xfce4-pulseaudio-plugin](https://gitlab.xfce.org/panel-plugins/xfce4-pulseaudio-plugin/-/blob/fd1e12412eec41a5cd787321f90222fd07da976c/panel-plugin/pulseaudio-notify.c#L141)
        * [xfce4-notifyd](https://gitlab.xfce.org/apps/xfce4-notifyd/-/blob/1d31872548887bfd5faf20fed136e68031fa98f0/xfce4-notifyd/xfce-notify-daemon.c#L1246)
