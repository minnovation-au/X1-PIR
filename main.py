import pycom

pycom.wdt_on_boot_timeout(360000)
pycom.wdt_on_boot(True)
pycom.heartbeat(False)

################## Start WLAN setup

SSID = 'AlphaX'
PSWD = 'A!phaXI0T'

################## End WLAN setup

import machine, ubinascii
import utime, network
from machine import Pin, Timer

from network import WLAN
wlan = WLAN()
wlan.deinit()

chrono = Timer.Chrono()
chrono.start()

sensorOn = machine.Pin('P23', mode=machine.Pin.OUT)
sensorOn(1)
sensorOn.hold(True)

mac=ubinascii.hexlify(machine.unique_id(),':').decode()
mac=mac.replace(":","")
print("Network ID: ",mac)

print(machine.wake_reason())
rst=machine.reset_cause()

def voltage():
    volts=0
    from machine import ADC
    adc = ADC()
    vpin = adc.channel(pin='P13')
    for i in range (0,999):
        volts+=vpin.voltage()
    return volts/i/0.24444/1000

def mqttPub(topic,msg):
    client.connect()
    client.publish(topic,msg)
    client.disconnect()

if (machine.wake_reason()[0])==1: #pin wakeup
        
    pycom.rgbled(0x7f0000) # green
    total_count = pycom.nvs_get('counter') +1
    pycom.nvs_set('counter', total_count)
        
    print('remaining deepsleep time is {}'.format(machine.remaining_sleep_time()))
    print('Counted: {} people'.format(total_count))

    while chrono.read() < 5:
        pass
        
    machine.pin_deepsleep_wakeup(pins = ['P8'], mode = machine.WAKEUP_ANY_HIGH, enable_pull = True)
        
    print("RST1: Wake & Sleep")
    pycom.rgbled(0)

    utime.sleep(0.5)
    if machine.remaining_sleep_time()-5000 < 1:
        sleeping = 1
    else:
        sleeping = machine.remaining_sleep_time()-5000

    machine.deepsleep(sleeping)

else: #RTC timer complete

    pycom.rgbled(0x007f00) # green
    # setup as a station
    wlan = network.WLAN(mode=network.WLAN.STA)
    wlan.connect(SSID, auth=(network.WLAN.WPA2, PSWD))
    while not wlan.isconnected():
        utime.sleep_ms(50)
        if chrono.read() > 20:
            print("no network")
            machine.deepsleep(60000)

    import socket       # Import socket module

    s = socket.socket()         # Create a socket object
    host = "192.168.4.1"           # Get local machine name
    port = 9999              # Reserve a port for your service.
    pycom.rgbled(0x00007f) # green
        
    total_count = pycom.nvs_get('counter')
    voltage = voltage()
    print('Sending Packet: {} people'.format(total_count))
        
    try:
        s.connect(("192.168.4.1", 9999))
    except Exception as e:
        print("Socket Error: ",e)

    try:
        s.send(bytes(mac+'/1/data|{"val":'+str(total_count)+',"volt":'+str(voltage)+'}','utf-8'))
    except:
        pass

    s.close()
    
    pycom.nvs_set('counter', 0)
        
    machine.pin_deepsleep_wakeup(pins = ['P8'], mode = machine.WAKEUP_ANY_HIGH, enable_pull = True)
        
    print("RST2: Send & Sleep")
    pycom.rgbled(0)
        
    utime.sleep(0.5)
    machine.deepsleep(300000)
