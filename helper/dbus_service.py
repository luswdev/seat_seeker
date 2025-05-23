import logging
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib, GObject

class combine_meta(type(dbus.service.Object), type(GObject.Object)):
    pass

class dbus_service(dbus.service.Object, GObject.Object, metaclass = combine_meta):
    __gsignals__ = {
        'add-config-signal': (GObject.SIGNAL_RUN_FIRST, None, (str, str, str, bool)),
        'del-config-signal': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'set-interval':      (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'announcement':      (GObject.SIGNAL_RUN_FIRST, None, (str, str)),
    }

    def __init__(self, object_path = '/com/luswdev/seatseeker'):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
        self.bus = dbus.SystemBus()
        self.bus_name = dbus.service.BusName("com.luswdev.seatseeker", bus = self.bus)
        GObject.Object.__init__(self)
        dbus.service.Object.__init__(self, self.bus, object_path)

    @dbus.service.method('com.luswdev.seatseeker', in_signature = 'sssb', out_signature = 'i')
    def addConfig(self, config, tag, channel, header):
        self.emit('add-config-signal', config, tag, channel, header)
        return 0

    @dbus.service.method('com.luswdev.seatseeker', in_signature = 's', out_signature = 'i')
    def delConfig(self, tag):
        self.emit('del-config-signal', tag)
        return 0

    @dbus.service.method('com.luswdev.seatseeker', in_signature = 'i', out_signature = 'i')
    def setInterval(self, interval):
        self.emit('set-interval', interval)
        return 0

    @dbus.service.method('com.luswdev.seatseeker', in_signature = 'ss', out_signature = 'i')
    def announcement(self, announcement, channel):
        self.emit('announcement', announcement, channel)
        return 0

    def start(self):
        logging.info("d-bus server is starting...")
        self.loop = GLib.MainLoop()
        self.loop.run()
