import logging
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib, GObject

class CombinedMeta(type(dbus.service.Object), type(GObject.Object)):
    pass

class dbus_service(dbus.service.Object, GObject.Object, metaclass=CombinedMeta):
    __gsignals__ = {
        'add-config-signal': (GObject.SIGNAL_RUN_FIRST, None, (str, str, str, bool)),
        'del-config-signal': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'set-interval': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self, object_path='/com/luswdev/seatseeker'):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.bus_name = dbus.service.BusName("com.luswdev.seatseeker", bus=self.bus)
        GObject.Object.__init__(self)
        dbus.service.Object.__init__(self, self.bus, object_path)

    @dbus.service.method('com.luswdev.seatseeker', in_signature='sssb', out_signature='i')
    def addConfig(self, config, tag, channel, header):
        self.emit('add-config-signal', config, tag, channel, header)
        return 0

    @dbus.service.method('com.luswdev.seatseeker', in_signature='s', out_signature='i')
    def delConfig(self, tag):
        self.emit('del-config-signal', tag)
        return 0

    @dbus.service.method('com.luswdev.seatseeker', in_signature='i', out_signature='i')
    def setInterval(self, interval):
        self.emit('set-interval', interval)
        return 0

    def start(self):
        logging.info("d-bus server is starting...")
        self.loop = GLib.MainLoop()
        self.loop.run()
