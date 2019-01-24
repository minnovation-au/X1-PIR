####################### GLOBAL SETUP ############################

SITE = '#####' ############################### Site Gateway Prefix
key = b'################################' ### Encryption Key

###################### Device Setup ############################

import machine, utime, ubinascii, socket, pycom, crypto, gc
from machine import I2C, deepsleep, Pin, Timer, WDT
from network import LoRa, WLAN
from crypto import AES

iv = crypto.getrandbits(128) # hardware generated random IV (never reuse it)

wdt = WDT(timeout=10000)  # enable it with a timeout of 2 seconds
gc.enable()

sensorOn = machine.Pin('P11', mode=machine.Pin.OUT)
sensorOn(1)
sensorOn.hold(True)

def mac():
    mac=ubinascii.hexlify(machine.unique_id(),':').decode()
    mac=mac.replace(":","")
    return(mac)
print("Network ID: ",mac())

def encrypt(send_pkg):
    cipher = AES(key, AES.MODE_CFB, iv)
    send_pkg = iv + cipher.encrypt(send_pkg)
    return(send_pkg)

def LoRaSend(val,ch):
    sl = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    sl.setblocking(True)
    sl.send(encrypt(SITE+mac()+'/'+ch+'&'+val)) # Send on LoRa Network & wait Reply
    sl.setblocking(False)
    try:
        pycom.nvs_set('msgID',pycom.nvs_get('msgID')+1)
    except:
        pycom.nvs_set('msgID',0)
    print("Sent",ch)

print(machine.wake_reason())
rst=machine.reset_cause()

def voltage():
    volts=0
    from machine import ADC
    adc = ADC()
    vpin = adc.channel(pin='P13')
    for i in range (0,999):
        volts+=vpin.voltage()/0.24444/1000
    print("volts/i)
    return volts/i


if (machine.wake_reason()[0])==1: #pin wakeup
        
    pycom.rgbled(0x7f0000) # green
    total_count = pycom.nvs_get('counter') +1
    pycom.nvs_set('counter', total_count)
        
    print('remaining deepsleep time is {}'.format(machine.remaining_sleep_time()))
    print('Counted: {} people'.format(total_count))

    while chrono.read() < 5:
        pass
        
    machine.pin_deepsleep_wakeup(pins = ['P10'], mode = machine.WAKEUP_ANY_HIGH, enable_pull = True)
        
    print("RST1: Wake & Sleep")
    pycom.rgbled(0)

    utime.sleep(0.5)
    if machine.remaining_sleep_time()-5000 < 1:
        sleeping = 1
    else:
        sleeping = machine.remaining_sleep_time()-5000

    machine.deepsleep(sleeping)

else: #RTC timer complete

    string = '{"val":'+str(pycom.nvs_get('counter'))+',"msgID":'+str(pycom.nvs_get('num'))+',"volt":'+str(voltage())+'}'
    LoRaSend(string,str(1))
    
    pycom.nvs_set('counter', 0)
        
    machine.pin_deepsleep_wakeup(pins = ['P10'], mode = machine.WAKEUP_ANY_HIGH, enable_pull = True)

    gc.collect()
    machine.deepsleep(3600000)
