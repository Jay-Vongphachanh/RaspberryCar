import dbus, dbus.mainloop.glib
from gi.repository import GObject
from example_advertisement import Advertisement
from example_advertisement import register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic
from example_gatt_server import register_app_cb, register_app_error_cb
import settings
import os, sys, select, termios, tty
import rospy
import json
import time
import Adafruit_PCA9685
from std_msgs.msg import String
#-------------------------------------------------------------------------------------------------------------
#-BELOW is the Code for the motor driving Similar to JoydriveRevision1.py without the ROS functionality 
#-USED for testing Purposes
carFreq = 97.1 # CHECK YOUR BOARD AGAINST OSCILLOSCOPE AND MAKE SURE IT IS AS C$
address = 0x40 # default is 0x40 
# If your board has a PWM module built in we will need the correct chip
#    import Adafruit_PCA9685
# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685(address)
pwm.set_pwm_freq(carFreq) #CHECK THE PWM OF YOUR BOARD AND FINE TUNE THIS #

def motor(data):
    print("I MADE IT THIS FAR",data[0],data[1])

    turn = data[0] #abs(0.05*data[0]-0.15)
    speed  =  data[1] #0.05*data[1]+0.15
    if speed > 0.15 and speed < 0.17:
	speed = 0.17    
    elif speed > 0.18:
	speed = 0.17
    pwm.set_pwm(8, 0, int(speed))
#    print("This is Motor values for 2.3 -SPEED:" , speed)
    setspeed23(8, speed)
#    print("This is Motor values for 2.3-TURN:" , turn)
    setspeed23(9,turn)

def setspeed23(pin, sped):
    pos = int(sped*4096)
    print(pos)
    pwm.set_pwm(pin, 0, pos)
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
# BELOW is the BlueTooth Code with edits for ROS publisher

BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
LOCAL_NAME =                   'RaspberryPi3_UART_jay_buster'
mainloop = None
 
class TxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False
        GObject.io_add_watch(sys.stdin, GObject.IO_IN, self.on_console_input)
 
    def on_console_input(self, fd, condition):
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True
 
    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
 
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
 
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False
 
class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)
 
    def WriteValue(self, value, options):
	getData = str(format(bytearray(value).decode()))
#	print("This is getting Published: ",getData, type(getData),len(getData))
        x,y = getData.split()
	print("the command value is..",x,y)
        data = [float(x),float(y)]
#	print("in array")
        motor(data) 
#	print("after motor")
#        sleep(0.1)
#        pub = rospy.Publisher('chatter', String, queue_size=10)
 #       rospy.init_node('talker', anonymous=True)
  #      pub.publish(command)
 
class UartService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self))
 
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
 
    def get_path(self):
        return dbus.ObjectPath(self.path)
 
    def add_service(self, service):
        self.services.append(service)
 
    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response
 
class UartApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0))
 
class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True
 
def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for o, props in objects.items():
        for iface in (LE_ADVERTISING_MANAGER_IFACE, GATT_MANAGER_IFACE):
            if iface not in props:
                continue
        return o
    return None
 
def main():
    os.system('sudo service bluetooth restart')
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)
    if not adapter:
        print('BLE adapter not found')
        return
 
    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)
 
    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)
 
    mainloop = GObject.MainLoop()
 
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb) 
    try:
        mainloop.run()
    except KeyboardInterrupt:
        adv.Release()
#--------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
