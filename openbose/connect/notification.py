from gi.repository import Notify, GLib


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